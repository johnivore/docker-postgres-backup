#!/bin/bash

# Copyright 2021 John Begenisich

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

set -e

if [ -z $BACKUP_PATH ]; then
    echo "** Required environment variable BACKUP_PATH not defined - should be set in Dockerfile"
    exit 1
fi

if [ -z $POSTGRES_HOST ]; then
    echo "** Required environment variable POSTGRES_HOST not defined"
    exit 1
fi
if [ -z $POSTGRES_PASSWORD ]; then
    echo "** Required environment variable POSTGRES_PASSWORD not defined"
    exit 1
fi

# optional vars
if [ -z $POSTGRES_PORT ]; then POSTGRES_PORT=5432; fi
if [ -z $POSTGRES_USER ]; then POSTGRES_USER=postgres; fi
if [ -z $BACKUP_KEEP_DAYS ]; then BACKUP_KEEP_DAYS=7; fi
if [ -z $TIMEZONE ]; then TIMEZONE="UTC"; fi

if [ ! -z $HEALTHCHECKS_URL ]; then
    HEALTHCHECKS_FLAG="--healthchecks-url $HEALTHCHECKS_URL"
else
    HEALTHCHECKS_FLAG=""
fi

if [ ! -z $BACKUP_AT_BOOT ] && [ "$BACKUP_AT_BOOT" == "true" ]; then
    BACKUP_AT_BOOT_FLAG="--backup-at-boot"
else
    BACKUP_AT_BOOT_FLAG=""
fi


PGPASS=/var/lib/postgresql/.pgpass
echo "Creating $PGPASS..."
echo "$POSTGRES_HOST:$POSTGRES_PORT:*:$POSTGRES_USER:$POSTGRES_PASSWORD" > $PGPASS
chown postgres:postgres $PGPASS
chmod 600 $PGPASS

echo "Starting backup scheduler..."
exec python3 -u /pgbackup.py \
        --backup-path $BACKUP_PATH \
        --keep-days $BACKUP_KEEP_DAYS \
        $HEALTHCHECKS_FLAG \
        $BACKUP_AT_BOOT_FLAG \
        --timezone $TIMEZONE
