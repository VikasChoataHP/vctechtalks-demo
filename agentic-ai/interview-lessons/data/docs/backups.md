# Nimbus Platform: Database Backups

## Backup schedule
All managed databases are backed up every night at 01:00 UTC. Backups are kept for 30 days and then deleted.

## Recovery targets
The recovery point objective (RPO) is 24 hours, so you can lose up to one day of data. The recovery time objective (RTO) is 4 hours.

## Restoring a database
To restore, raise a restore ticket with the database name and the backup date. Restores always go to a new database first so you can check the data before switching your app to it.
