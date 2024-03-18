import logging
import os

from quart import Quart
from quart_schema import QuartSchema


def create_app():
    if os.getenv("RUNNING_IN_PRODUCTION"):
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.DEBUG)

    app = Quart(__name__)
    QuartSchema(app)

    from . import chat  # noqa

    app.register_blueprint(chat.bp)

    return app
