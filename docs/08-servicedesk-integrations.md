# Service Desk Integrations

The gateway ships mock defaults plus real connectors for ServiceNow, Remedy, and Jira Service Management behind feature flags. All secrets stay on the backend.

## ServiceNow
- **Auth**: OAuth client credentials (`SERVICENOW_INSTANCE_URL`, `SERVICENOW_CLIENT_ID`, `SERVICENOW_CLIENT_SECRET`).
- **Scopes**: incident create/read/update via Table API.
- **Mapping**: `incident.number` → `id`, `short_description` → `title`.
- **Webhooks**: use outbound REST or ServiceNow events to notify the gateway on status changes.

## Remedy
- **Auth**: Basic auth or token (`REMEDY_BASE_URL`, `REMEDY_USERNAME`, `REMEDY_PASSWORD`).
- **Scopes**: incident create and status lookup.
- **Mapping**: `Incident Number` → `id`, `Notes` → `comment`.
- **Webhooks**: Remedy webhook to post to `/v1/chat` with status context (future).

## Jira Service Management
- **Auth**: PAT or OAuth (`JIRA_BASE_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN`).
- **Scopes**: service request create, comment, status.
- **Mapping**: `issue.key` → `id`, `summary` → `title`.
- **Webhooks**: Atlassian webhooks for transitions and comments.
