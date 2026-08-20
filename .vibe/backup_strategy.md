# MemoryChat PostgreSQL Backup and Restore Strategy

This document outlines the standard operating procedures for backing up and restoring the MemoryChat PostgreSQL database. This is a critical requirement before the first production deployment.

## 1. Backup Strategy

The database will be backed up using `pg_dump`. 

### Automated Backups
It is recommended to configure an automated cron job or use a managed database service (e.g., AWS RDS, Supabase) that provides automated daily snapshots and Point-in-Time Recovery (PITR).

### Manual Logical Backup
To take a manual snapshot of the database schema and data, run the following command on the database server or a machine with `pg_dump` installed and access to the DB:

```bash
pg_dump -U <username> -h <host> -d <database_name> -F c -f memorychat_backup_$(date +%F).dump
```
- `-F c`: Creates a custom-format archive suitable for input into `pg_restore`. This format is compressed and allows for parallel restoration.
- `-f`: Specifies the output file.

Store the generated `.dump` file in a secure, off-site storage location (e.g., AWS S3).

## 2. Restore Procedure

To restore the database from a `.dump` backup in the event of data loss or when cloning the environment for testing:

**WARNING:** Restoring over an existing database will overwrite current data.

### Step-by-step Restore
1. Terminate all active application connections to the database to prevent partial writes during restoration.
2. If necessary, drop and recreate the database:
   ```bash
   dropdb -U <username> -h <host> <database_name>
   createdb -U <username> -h <host> <database_name>
   ```
3. Run `pg_restore`:
   ```bash
   pg_restore -U <username> -h <host> -d <database_name> -1 -j 4 memorychat_backup_YYYY-MM-DD.dump
   ```
   - `-1`: Executes the restore as a single transaction. If an error occurs, the entire restore is rolled back.
   - `-j 4`: Uses 4 concurrent jobs to speed up the restoration.

## 3. Disaster Recovery Validation

Before deploying to production, this backup and restore cycle MUST be tested:
1. Generate test data (users, connections, messages) in a staging environment.
2. Execute the `pg_dump` command.
3. Drop the staging database and recreate it.
4. Execute the `pg_restore` command.
5. Boot the MemoryChat application and verify that messages and connections are intact.
