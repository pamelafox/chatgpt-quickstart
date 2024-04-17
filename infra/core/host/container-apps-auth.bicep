metadata description = 'Creates an Azure Container Apps Auth Config using Microsoft Entra as Identity Provider.'

@description('The name of the container apps resource within the current resource group scope')
param name string

@description('The client ID of the Microsoft Entra application.')
param clientId string

// the issuer is different depending if we are in a workforce or external tenant
param openIdIssuer string

resource app 'Microsoft.App/containerApps@2023-05-01' existing = {
  name: name
}

resource auth 'Microsoft.App/containerApps/authConfigs@2023-05-01' = {
  parent: app
  name: 'current'
  properties: {
    platform: {
      enabled: true
    }
    globalValidation: {
      redirectToProvider: 'azureactivedirectory'
      unauthenticatedClientAction: 'RedirectToLoginPage'
    }
    identityProviders: {
      azureActiveDirectory: {
        registration: {
          clientId: clientId
          openIdIssuer: openIdIssuer
          clientSecretSettingName: 'OVERRIDE_USE_MI_FIC_ASSERTION_CLIENTID'
        }
      }
    }
  }
}
