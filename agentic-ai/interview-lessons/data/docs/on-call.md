# Nimbus Platform: Incidents and On-Call

## Severity levels
- P1: a customer-facing service is down or badly degraded for all users.
- P2: a service is degraded for some users, or there is a security incident.
- P3: a problem with a workaround, no customer impact.
- P4: a question or minor issue.

## Response times
The on-call engineer must acknowledge a P1 within 15 minutes and a P2 within 30 minutes. P3 issues are handled within 1 business day and P4 within 3 business days.

## Paging
Incidents are paged through Beacon. If the primary on-call engineer does not acknowledge in time, Beacon escalates to the secondary, and then to the engineering manager.

## Raising an incident
Open an incident ticket with a short title, the affected service, and the severity. For P1 and P2, also post in the #incidents channel.
