using './main.bicep'

param azureOpenAIAccountName = 'replace-with-openai-account'
param azureOpenAIChatDeployment = 'replace-with-chat-deployment'
param azureOpenAIEmbeddingDeployment = 'replace-with-embedding-deployment'
param collectionId = 'sample-collection'
param environmentName = 'dev'
param imageTag = 'local'
param oidcAudience = 'api://replace-with-application-id'
param oidcIssuer = 'https://login.microsoftonline.com/replace-with-tenant-id/v2.0'
param prefix = 'shaper'
param scannerImage = 'clamav/clamav-debian:1.4.3'
param shouldDeployApp = false
