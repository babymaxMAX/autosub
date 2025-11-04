#!/bin/bash

# Restore database script
BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file>"
    echo "Example: $0 backups/backup_20240101_120000.sql.gz"
    exit 1
fi

if [ ! -f "$BACKUP_FILE" ]; then
    echo "Error: Backup file not found: $BACKUP_FILE"
    exit 1
fi

echo "Restoring database from: $BACKUP_FILE"
echo "WARNING: This will overwrite the current database!"
read -p "Continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Restore cancelled"
    exit 0
fi

# Decompress if needed
if [[ $BACKUP_FILE == *.gz ]]; then
    echo "Decompressing backup..."
    gunzip -c $BACKUP_FILE > /tmp/restore.sql
    RESTORE_FILE="/tmp/restore.sql"
else
    RESTORE_FILE=$BACKUP_FILE
fi

# Restore database
echo "Restoring database..."
docker-compose exec -T postgres psql -U autosub autosub < $RESTORE_FILE

if [ $? -eq 0 ]; then
    echo "✓ Database restored successfully"
    
    # Cleanup
    if [ -f "/tmp/restore.sql" ]; then
        rm /tmp/restore.sql
    fi
else
    echo "✗ Restore failed"
    exit 1
fi

