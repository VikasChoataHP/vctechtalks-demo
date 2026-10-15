# Nimbus Platform: Deployment Guide

## How to deploy
Use the `nimbus deploy` command from your service repository. It builds the container image, runs the security scan, and rolls the new version out to the target environment. Every service has three environments: dev, staging, and prod.

## Production approvals
Deployments to prod need an approved change ticket. Add the ticket number with `nimbus deploy --env prod --change CHG-1234`. Deployments to dev and staging do not need a change ticket.

## Deployment freeze
Production deployments are frozen every week from Friday 6 PM to Monday 9 AM India time. During the freeze only emergency fixes for P1 incidents are allowed, and they need approval from the on-call platform lead.

## Rollback
If a release misbehaves, run `nimbus rollback --env prod`. It redeploys the previous image within about two minutes. Rollbacks do not need a new change ticket, but you must update the original ticket with the reason.
