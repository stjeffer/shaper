metadata name = 'Azure OpenAI role assignment'
metadata description = 'Grants one managed identity access to an existing Azure OpenAI account.'

targetScope = 'resourceGroup'

@description('Existing Azure OpenAI account name.')
param accountName string

@description('Managed identity principal identifier.')
param principalId string

@description('Cognitive Services OpenAI User role definition resource ID.')
param roleDefinitionId string

resource account 'Microsoft.CognitiveServices/accounts@2024-10-01' existing = {
  name: accountName
}

resource assignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(account.id, principalId, roleDefinitionId)
  scope: account
  properties: {
    principalId: principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: roleDefinitionId
  }
}

@description('Created role assignment resource ID.')
output roleAssignmentId string = assignment.id
