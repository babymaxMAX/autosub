#!/bin/bash

# Backup database script
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="./backups"

# Create backup directory
mkdir -p $BACKUP_DIR

echo "Creating database backup..."

# Backup using docker-compose
docker-compose exec -T postgres pg_dump -U autosub autosub > $BACKUP_DIR/backup_$DATE.sql

if [ $? -eq 0 ]; then
    echo "✓ Backup created: $BACKUP_DIR/backup_$DATE.sql"
    
    # Compress backup
    gzip $BACKUP_DIR/backup_$DATE.sql
    echo "✓ Backup compressed: $BACKUP_DIR/backup_$DATE.sql.gz"
    
    # Remove old backups (older than 7 days)
    find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete
    echo "✓ Old backups removed"
else
    echo "✗ Backup failed"
    exit 1
fi

