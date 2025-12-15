# Service Desk Integrations

The gateway stubs ServiceNow, Remedy, and Jira Service Management with a consistent ticket contract so downstream systems can be swapped without UI changes.

## ServiceNow
- **Auth**: OAuth or PAT in production; stubbed locally.
- **Scopes**: incident create/read/update.
- **Mapping**: `incident.number` → `id`, `short_description` → `title`.
- **Webhooks**: use outbound REST or ServiceNow events to notify the gateway on status changes.

## Remedy
- **Auth**: OAuth or API token.
- **Scopes**: incident create and status lookup.
- **Mapping**: `Incident Number` → `id`, `Notes` → `comment`.
- **Webhooks**: Remedy webhook to post to `/v1/chat` with status context (future).

## Jira Service Management
- **Auth**: OAuth or PAT.
- **Scopes**: service request create, comment, status.
- **Mapping**: `issue.key` → `id`, `summary` → `title`.
- **Webhooks**: Atlassian webhooks for transitions and comments.
