metadata name = 'Shaper Azure Container Apps'
metadata description = 'Deploys the Shaper service, persistent state, registry, identity, and monitoring.'

targetScope = 'resourceGroup'

/*
 * Common parameters
 */

@description('Deployment environment name.')
param environmentName 'dev' | 'test' | 'prod'

@description('Azure region for all resources.')
param location string = resourceGroup().location

@description('Short resource-name prefix.')
@minLength(3)
@maxLength(12)
param prefix string

@description('Tags applied to resources.')
param tags {
  environment: string
  application: string
} = {
  environment: environmentName
  application: 'shaper'
}

/*
 * Application parameters
 */

@description('Existing Azure OpenAI account name.')
param azureOpenAIAccountName string

@description('Azure OpenAI chat model deployment name.')
param azureOpenAIChatDeployment string

@description('Azure OpenAI embedding model deployment name.')
param azureOpenAIEmbeddingDeployment string

@description('Resource group containing the existing Azure OpenAI account.')
param azureOpenAIResourceGroupName string = resourceGroup().name

@description('Collection identifier served by this deployment.')
param collectionId string

@description('Container image tag to deploy from the provisioned registry.')
param imageTag string

@description('OIDC audience accepted by the service.')
param oidcAudience string

@description('OIDC issuer used to validate inbound tokens.')
param oidcIssuer string

@description('Microsoft Entra application client ID used for interactive browser sign-in.')
param entraClientId string

@secure()
@description('Microsoft Entra application secret used by Container Apps authentication.')
param entraClientSecret string

@description('Tenant ID granted initial Shaper collection administration.')
param bootstrapTenantId string

@description('Object ID granted initial Shaper collection administration.')
param bootstrapPrincipalId string

@secure()
@description('Administrator password for the Shaper PostgreSQL server.')
param postgresAdministratorPassword string

@description('Whether to deploy the Container App after its image has been built.')
param shouldDeployApp bool = true

/*
 * Security and state parameters
 */

@description('Approved ClamAV image reference. Production deployments should use an immutable digest.')
param scannerImage string

@description('Persistent Azure Files share quota in GiB.')
@minValue(10)
@maxValue(5120)
param stateShareQuotaGiB int = 100

/*
 * Variables
 */

var containerAppName = 'ca-${prefix}-${environmentName}'
var containerEnvironmentName = 'cae-${prefix}-${environmentName}'
var identityName = 'id-${prefix}-${environmentName}'
var postgresName = take(replace('psql-${prefix}-${environmentName}-${uniqueString(resourceGroup().id)}', '_', '-'), 63)
var registryName = take(replace('cr${prefix}${environmentName}${uniqueString(resourceGroup().id)}', '-', ''), 50)
var shareName = 'shaper-state'
var storageName = take(replace('st${prefix}${environmentName}${uniqueString(resourceGroup().id)}', '-', ''), 24)
var workspaceName = 'log-${prefix}-${environmentName}'
var acrPullRoleDefinitionId = subscriptionResourceId(
  'Microsoft.Authorization/roleDefinitions',
  '7f951dda-4ed3-4680-a7ca-43fe172d538d'
)
var openAIUserRoleDefinitionId = subscriptionResourceId(
  'Microsoft.Authorization/roleDefinitions',
  '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd'
)

/*
 * Resources
 */

resource workspace 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: workspaceName
  location: location
  tags: tags
  properties: {
    retentionInDays: 30
    features: {
      enableLogAccessUsingOnlyResourcePermissions: true
    }
  }
}

resource registry 'Microsoft.ContainerRegistry/registries@2023-07-01' = {
  #disable-next-line BCP334
  name: registryName
  location: location
  tags: tags
  sku: {
    name: 'Basic'
  }
  properties: {
    adminUserEnabled: false
    publicNetworkAccess: 'Enabled'
  }
}

resource identity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: identityName
  location: location
  tags: tags
}

resource registryPull 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(registry.id, identity.id, acrPullRoleDefinitionId)
  scope: registry
  properties: {
    principalId: identity.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: acrPullRoleDefinitionId
  }
}

module openAIUser './modules/openai-role.bicep' = {
  scope: resourceGroup(azureOpenAIResourceGroupName)
  params: {
    accountName: azureOpenAIAccountName
    principalId: identity.properties.principalId
    roleDefinitionId: openAIUserRoleDefinitionId
  }
}

resource storage 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  #disable-next-line BCP334
  name: storageName
  location: location
  tags: tags
  kind: 'StorageV2'
  sku: {
    name: 'Standard_LRS'
  }
  properties: {
    allowBlobPublicAccess: false
    allowSharedKeyAccess: true
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
  }
}

resource fileService 'Microsoft.Storage/storageAccounts/fileServices@2023-05-01' = {
  parent: storage
  name: 'default'
}

resource stateShare 'Microsoft.Storage/storageAccounts/fileServices/shares@2023-05-01' = {
  parent: fileService
  name: shareName
  properties: {
    enabledProtocols: 'SMB'
    shareQuota: stateShareQuotaGiB
  }
}

resource containerEnvironment 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: containerEnvironmentName
  location: location
  tags: tags
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: workspace.properties.customerId
        sharedKey: workspace.listKeys().primarySharedKey
      }
    }
  }
}

resource environmentStorage 'Microsoft.App/managedEnvironments/storages@2024-03-01' = {
  parent: containerEnvironment
  name: 'state'
  properties: {
    azureFile: {
      accessMode: 'ReadWrite'
      accountKey: storage.listKeys().keys[0].value
      accountName: storage.name
      shareName: stateShare.name
    }
  }
}

resource postgres 'Microsoft.DBforPostgreSQL/flexibleServers@2023-12-01-preview' = {
      #disable-next-line BCP334
      name: postgresName
      location: location
      tags: tags
      sku: {
        name: 'Standard_B1ms'
        tier: 'Burstable'
      }
      properties: {
        administratorLogin: 'shaperadmin'
        administratorLoginPassword: postgresAdministratorPassword
        authConfig: {
          activeDirectoryAuth: 'Disabled'
          passwordAuth: 'Enabled'
        }
        backup: {
          backupRetentionDays: 7
          geoRedundantBackup: 'Disabled'
        }
        highAvailability: {
          mode: 'Disabled'
        }
        storage: {
          storageSizeGB: 32
        }
        version: '16'
      }
    }

resource postgresDatabase 'Microsoft.DBforPostgreSQL/flexibleServers/databases@2023-12-01-preview' = {
      parent: postgres
      name: 'shaper'
      properties: {
        charset: 'UTF8'
        collation: 'en_US.utf8'
      }
    }

resource postgresAzureAccess 'Microsoft.DBforPostgreSQL/flexibleServers/firewallRules@2023-12-01-preview' = {
      parent: postgres
      name: 'AllowAzureServices'
      properties: {
        startIpAddress: '0.0.0.0'
        endIpAddress: '0.0.0.0'
  }
}

resource containerApp 'Microsoft.App/containerApps@2024-03-01' = if (shouldDeployApp) {
  name: containerAppName
  location: location
  tags: tags
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${identity.id}': {}
    }
  }
  properties: {
    environmentId: containerEnvironment.id
    configuration: {
      activeRevisionsMode: 'Single'
      secrets: [
        {
          name: 'entra-client-secret'
          value: entraClientSecret
        }
        {
          name: 'postgres-url'
          value: 'postgresql://shaperadmin:${uriComponent(postgresAdministratorPassword)}@${postgres.properties.fullyQualifiedDomainName}:5432/shaper?sslmode=require'
        }
      ]
      ingress: {
        allowInsecure: false
        external: true
        targetPort: 8000
        transport: 'auto'
      }
      registries: [
        {
          identity: identity.id
          server: registry.properties.loginServer
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'shaper'
          image: '${registry.properties.loginServer}/shaper:${imageTag}'
          env: [
            {
              name: 'AZURE_CLIENT_ID'
              value: identity.properties.clientId
            }
            {
              name: 'SHAPER_AZURE_OPENAI_DEPLOYMENT'
              value: azureOpenAIChatDeployment
            }
            {
              name: 'SHAPER_AZURE_OPENAI_EMBEDDING_DEPLOYMENT'
              value: azureOpenAIEmbeddingDeployment
            }
            {
              name: 'SHAPER_AZURE_OPENAI_ENDPOINT'
              value: 'https://${azureOpenAIAccountName}.openai.azure.com/'
            }
            {
              name: 'SHAPER_AZURE_OPENAI_USE_MANAGED_IDENTITY'
              value: 'true'
            }
            {
              name: 'SHAPER_BOOTSTRAP_PRINCIPAL_ID'
              value: bootstrapPrincipalId
            }
            {
              name: 'SHAPER_BOOTSTRAP_TENANT_ID'
              value: bootstrapTenantId
            }
            {
              name: 'SHAPER_CLAMD_HOST'
              value: '127.0.0.1'
            }
            {
              name: 'SHAPER_COLLECTION_ID'
              value: collectionId
            }
            {
              name: 'SHAPER_DATABASE_PATH'
              value: ':memory:'
            }
            {
              name: 'SHAPER_OIDC_AUDIENCE'
              value: oidcAudience
            }
            {
              name: 'SHAPER_OIDC_ISSUER'
              value: oidcIssuer
            }
            {
              name: 'SHAPER_POSTGRES_URL'
              secretRef: 'postgres-url'
            }
            {
              name: 'SHAPER_PROFILE'
              value: 'production'
            }
            {
              name: 'SHAPER_SQLITE_JOURNAL_MODE'
              value: 'DELETE'
            }
            {
              name: 'SHAPER_MODEL_PROVIDER'
              value: 'azure_openai'
            }
            {
              name: 'SHAPER_PUBLIC_URL'
              value: 'https://${containerAppName}.${containerEnvironment.properties.defaultDomain}'
            }
            {
              name: 'SHAPER_TRUST_INGRESS_IDENTITY'
              value: 'true'
            }
          ]
          probes: [
            {
              type: 'Liveness'
              httpGet: {
                path: '/health/live'
                port: 8000
                scheme: 'HTTP'
              }
              initialDelaySeconds: 10
              periodSeconds: 30
            }
            {
              type: 'Readiness'
              httpGet: {
                path: '/health/ready'
                port: 8000
                scheme: 'HTTP'
              }
              initialDelaySeconds: 20
              periodSeconds: 10
            }
          ]
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
          volumeMounts: [
            {
              mountPath: '/mnt/state'
              volumeName: 'state'
            }
          ]
        }
        {
          name: 'clamd'
          image: scannerImage
          resources: {
            cpu: json('1.0')
            memory: '2Gi'
          }
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 1
      }
      volumes: [
        {
          name: 'state'
          storageName: environmentStorage.name
          storageType: 'AzureFile'
        }
      ]
    }
  }
  dependsOn: [
    openAIUser
    postgresDatabase
    postgresAzureAccess
    registryPull
  ]
}

resource containerAppAuth 'Microsoft.App/containerApps/authConfigs@2024-03-01' = if (shouldDeployApp) {
  parent: containerApp
  name: 'current'
  properties: {
    globalValidation: {
      excludedPaths: [
        '/health/*'
        '/mcp/*'
        '/v1/demo/analysis'
      ]
      redirectToProvider: 'azureactivedirectory'
      unauthenticatedClientAction: 'RedirectToLoginPage'
    }
    identityProviders: {
      azureActiveDirectory: {
        registration: {
          clientId: entraClientId
          clientSecretSettingName: 'entra-client-secret'
          openIdIssuer: oidcIssuer
        }
        validation: {
          allowedAudiences: [
            entraClientId
            oidcAudience
          ]
        }
      }
    }
    platform: {
      enabled: true
    }
  }
}

/*
 * Outputs
 */

@description('Container App fully qualified domain name.')
output applicationFqdn string? = containerApp.?properties.?configuration.?ingress.?fqdn

@description('Latest Container App revision name.')
output applicationRevision string? = containerApp.?properties.?latestRevisionName

@description('Provisioned Azure Container Registry login server.')
output registryLoginServer string = registry.properties.loginServer

@description('Provisioned Azure Container Registry name.')
output registryName string = registry.name

@description('User-assigned managed identity resource ID.')
output managedIdentityId string = identity.id

@description('Provisioned PostgreSQL server name.')
output postgresServerName string = postgres.name
