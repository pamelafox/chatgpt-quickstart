import json
import os
from dataclasses import dataclass

import azure.identity.aio
import openai
from quart import (
    Blueprint,
    Response,
    current_app,
    render_template,
    stream_with_context,
)
from quart_schema import validate_request

bp = Blueprint("chat", __name__, template_folder="templates", static_folder="static")


@bp.before_app_serving
async def configure_openai():
    client_args = {}
    if os.getenv("LOCAL_OPENAI_ENDPOINT"):
        # Use a local endpoint like llamafile server
        current_app.logger.info("Using local OpenAI-compatible API with no key")
        client_args["api_key"] = "no-key-required"
        client_args["base_url"] = os.getenv("LOCAL_OPENAI_ENDPOINT")
        bp.openai_client = openai.AsyncOpenAI(
            **client_args,
        )
    else:
        # Use an Azure OpenAI endpoint instead,
        # either with a key or with keyless authentication
        if os.getenv("AZURE_OPENAI_KEY"):
            # Authenticate using an Azure OpenAI API key
            # This is generally discouraged, but is provided for developers
            # that want to develop locally inside the Docker container.
            current_app.logger.info("Using Azure OpenAI with key")
            client_args["api_key"] = os.getenv("AZURE_OPENAI_KEY")
        else:
            if client_id := os.getenv("AZURE_OPENAI_CLIENT_ID"):
                # Authenticate using a user-assigned managed identity on Azure
                # See aca.bicep for value of AZURE_OPENAI_CLIENT_ID
                current_app.logger.info(
                    "Using Azure OpenAI with managed identity for client ID %s",
                    client_id,
                )
                default_credential = azure.identity.aio.ManagedIdentityCredential(client_id=client_id)
            else:
                # Authenticate using the default Azure credential chain
                # See https://docs.microsoft.com/azure/developer/python/azure-sdk-authenticate#defaultazurecredential
                # This will *not* work inside a Docker container.
                current_app.logger.info("Using Azure OpenAI with default credential")
                default_credential = azure.identity.aio.DefaultAzureCredential(
                    exclude_shared_token_cache_credential=True
                )
            client_args["azure_ad_token_provider"] = azure.identity.aio.get_bearer_token_provider(
                default_credential, "https://cognitiveservices.azure.com/.default"
            )
        bp.openai_client = openai.AsyncAzureOpenAI(
            api_version="2023-07-01-preview",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            **client_args,
        )


@bp.after_app_serving
async def shutdown_openai():
    await bp.openai_client.close()


@bp.get("/")
async def index():
    return await render_template("index.html")


@dataclass
class ChatRequest:
    message: str


@dataclass
class ChatResponseHeaders:
    transfer_encoding: str = "chunked"
    content_type: str = "application/json-lines"


@bp.post("/chat")
@validate_request(ChatRequest)
# @validate_response(List[ChatCompletionChunk], 200, ChatResponseHeaders)
async def chat_handler(data: ChatRequest):
    request_message = data.message

    @stream_with_context
    async def response_stream():
        chat_coroutine = bp.openai_client.chat.completions.create(
            # Azure Open AI takes the deployment name as the model name
            model=os.environ["AZURE_OPENAI_CHATGPT_DEPLOYMENT"],
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": request_message},
            ],
            stream=True,
        )
        try:
            async for event in await chat_coroutine:
                yield json.dumps(event.model_dump(), ensure_ascii=False) + "\n"
        except Exception as e:
            current_app.logger.error(e)
            yield json.dumps({"error": str(e)}, ensure_ascii=False) + "\n"

    return Response(response_stream(), mimetype="application/json-lines")
