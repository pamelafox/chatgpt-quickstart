targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('Name which is used to generate a short unique hash for each resource')
param name string

@minLength(1)
@description('Primary location for all resources')
param location string

@description('Id of the user or app to assign application roles')
param principalId string = ''

@description('Flag to decide where to create OpenAI role for current user')
param createRoleForUser bool = true

param acaExists bool = false

param openAiResourceName string = ''
param openAiResourceGroupName string = ''
param openAiResourceGroupLocation string = ''
param openAiSkuName string = ''
param openAiDeploymentCapacity int = 30
param openAiApiVersion string = ''

param useAuthentication bool = false

param tenantId string = ''
param loginEndpoint string = ''

var resourceToken = toLower(uniqueString(subscription().id, name, location))
var tags = { 'azd-env-name': name }

var rgName = '${name}-rg'

resource resourceGroup 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: rgName
  location: location
  tags: tags
}

var prefix = '${name}-${resourceToken}'


module logAnalyticsWorkspace 'core/monitor/loganalytics.bicep' = {
  name: 'loganalytics'
  scope: resourceGroup
  params: {
    name: '${prefix}-loganalytics'
    location: location
    tags: tags
  }
}



// Container apps host (including container registry)
module containerApps 'core/host/container-apps.bicep' = {
  name: 'container-apps'
  scope: resourceGroup
  params: {
    name: 'app'
    location: location
    tags: tags
    containerAppsEnvironmentName: '${prefix}-containerapps-env'
    containerRegistryName: '${replace(prefix, '-', '')}registry'
    logAnalyticsWorkspaceName: logAnalyticsWorkspace.outputs.name
  }
}

// Container app frontend
module aca 'aca.bicep' = {
  name: 'aca'
  scope: resourceGroup
  params: {
    name: replace('${take(prefix,19)}-ca', '--', '-')
    location: location
    tags: tags
    identityName: '${prefix}-id-aca'
    containerAppsEnvironmentName: containerApps.outputs.environmentName
    containerRegistryName: containerApps.outputs.registryName
    exists: acaExists
  }
}

module registration 'appregistration.bicep' = if (useAuthentication) {
  name: 'reg'
  scope: resourceGroup
  params: {
    keyVaultName: '${take(prefix, 21)}-kv'
    location: location
    tags: tags
    principalId: principalId
    appEndpoint: aca.outputs.SERVICE_ACA_URI
  }
}

module auth 'core/host/container-apps-auth.bicep' = if (useAuthentication) {
  name: 'aca-container-apps-auth-module'
  scope: resourceGroup
  params: {
    name: aca.outputs.SERVICE_ACA_NAME
    clientId: registration.outputs.clientAppId
    clientCertificateThumbprint: registration.outputs.certThumbprint
    openIdIssuer: empty(tenantId) ? '${environment().authentication.loginEndpoint}${tenant().tenantId}/v2.0' : 'https://${loginEndpoint}/${tenantId}/v2.0'

  }
}

output AZURE_LOCATION string = location

output SERVICE_ACA_IDENTITY_PRINCIPAL_ID string = aca.outputs.SERVICE_ACA_IDENTITY_PRINCIPAL_ID
output SERVICE_ACA_NAME string = aca.outputs.SERVICE_ACA_NAME
output SERVICE_ACA_URI string = aca.outputs.SERVICE_ACA_URI
output SERVICE_ACA_IMAGE_NAME string = aca.outputs.SERVICE_ACA_IMAGE_NAME

output AZURE_CONTAINER_ENVIRONMENT_NAME string = containerApps.outputs.environmentName
output AZURE_CONTAINER_REGISTRY_ENDPOINT string = containerApps.outputs.registryLoginServer
output AZURE_CONTAINER_REGISTRY_NAME string = containerApps.outputs.registryName
