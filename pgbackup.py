#!/usr/bin/python

"""
Simple Postgresql backup script, designed to be run in a container.

Host, username, password & port should be set in ~/.pgpass.

Copyright 2022 John Begenisich

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import argparse
import gzip
import socket
import subprocess
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

from apscheduler.schedulers.blocking import BlockingScheduler


# global var set by CLI option
HEALTHCHECKS_URL = None


def log(message: str) -> None:
    """This is docker; log to stdout."""
    now: str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f'[{now}] {message}')


def run(command: str, dry_run: bool = False, die_on_failure: bool = True) -> None:
    if dry_run:
        log(f'Dry run: {command}')
        return
    result = subprocess.run(command, shell=True)
    if result.returncode != 0 and die_on_failure:
        fail()


def healthchecks_ping(url: str) -> bool:
    log(f'Pinging {url}')
    try:
        urllib.request.urlopen(url, timeout=20)
    except socket.error as exception:
        log(f'** Failed pinging {url}: {exception}')
        return False
    return True


def fail() -> None:
    """Ping healthchecks fail URL."""
    if HEALTHCHECKS_URL:
        healthchecks_ping(f'{HEALTHCHECKS_URL}/fail')


def clean_old_backups(backup_path: Path, keep_days: int) -> None:
    run(f'find {backup_path} -type f -prune -mtime +{keep_days} -exec rm -f {{}} \;')


def get_uncompressed_gzip_size(filename: Path) -> int:
    with gzip.open(filename, 'rb') as fd:
        fd.seek(0, 2)
        size = fd.tell()
    return size


def backup_postgresql(backup_path: Path) -> bool:
    # get hostname from .pgpass
    with open(Path.home() / '.pgpass') as reader:
        pgpass_line = reader.readline().strip()
    hostname: str = pgpass_line.split(':')[0]
    datestr: str = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename: Path = backup_path / f'{datestr}.sql.gz'
    command: str = f'pg_dumpall -c -h {hostname} | gzip > {filename}'
    log(f'Backup started: {command}')
    run(command)
    # NOTE: Gzip will think we've succeeded, so we'll get a return code of 0.
    # Do some extra checks just to be careful
    if not filename.is_file():
        print(f'** Backup failed! {filename} not found.')
        fail()
        return False
    backup_size: int = filename.stat().st_size
    if backup_size == 0:
        print(f'** Backup failed! {filename} is empty; deleting.')
        filename.unlink()
        fail()
        return False
    # If pg_dumpall failed, the uncompressed backup size will likely be 0
    uncompressed_size = get_uncompressed_gzip_size(filename)
    if uncompressed_size == 0:
        print('** Backup failed! Uncompressed backup size is 0; deleting.')
        filename.unlink()
        fail()
        return False
    log(f'Backup complete. {filename} size: {backup_size}; uncompressed size: {uncompressed_size}')
    return True


def backup(backup_path: Path, keep_days: int):
    if HEALTHCHECKS_URL:
        healthchecks_ping(f'{HEALTHCHECKS_URL}/start')

    backup_postgresql(backup_path)

    if keep_days > 0:
        log(f'Pruning old backups - retaining {keep_days} days of backups')
        clean_old_backups(backup_path, keep_days)

    # success
    if HEALTHCHECKS_URL:
        healthchecks_ping(f'{HEALTHCHECKS_URL}')

    log('Done.')


def main() -> None:
    parser = argparse.ArgumentParser(description='Simple Postgresql backup script for Docker')
    parser.add_argument('--backup-path', '-p', type=str, default='/backups')
    parser.add_argument('--keep-days', '-k', type=int, default=7)
    parser.add_argument('--healthchecks-url', type=str)
    parser.add_argument('--backup-at-boot', action='store_true')
    parser.add_argument('--timezone', type=str, default='UTC')
    args = parser.parse_args()

    global HEALTHCHECKS_URL
    HEALTHCHECKS_URL = args.healthchecks_url

    backup_path = Path(args.backup_path)
    if not backup_path.is_dir():
        print(f'** {backup_path} not found!')
        fail()
        sys.exit(1)

    log('Backup scheduler starting')
    print(f'  backup destination: {backup_path}')
    print(f'  timezone: {args.timezone}')
    if args.keep_days > 0:
        print(f'  retain {args.keep_days} days of backups')
    else:
        print(f'  keep old backups forever')
    if args.healthchecks_url:
        print(f'  healthchecks ping URL: {args.healthchecks_url}')
    else:
        print('  no healthchecks ping URL specified')

    if args.backup_at_boot:
        log('Running backup now because --backup-now was specified')
        backup(backup_path, 0)  # don't delete any backups this time

    scheduler = BlockingScheduler(timezone=args.timezone)
    scheduler.add_job(lambda: backup(backup_path, args.keep_days),
                      'interval', days=1)
    scheduler.start()


if __name__ == '__main__':
    main()
