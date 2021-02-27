# docker-postgres-backup

A simple, multi-arch Docker image to make full backups of Postgresql servers.  All recent Postgresql versions are supported.

* Git repo: <https://gitlab.com/johnivore/docker-postgresl-backup>
* Dockerhub: <https://hub.docker.com/r/johnivore/postgres-backup/>


## Usage

### Example docker-compose

```yaml
services:
  pgbackup:
    image: johnivore/13-alpine-latest
    container_name: "pgbackup"
    restart: "unless-stopped"
    volumes:
      - "/srv/pgbackups:/backups"
    environment:
      - "POSTGRES_HOST=postgres.example.com"        # required
      - "POSTGRES_PORT=5432"                        # default: 5432
      - "POSTGRES_USER=postgres"                    # default: postgres
      - "POSTGRES_PASSWORD=purplemonkeydishwasher"  # required
      - "TIMEZONE=Asia/Shanghai"                    # default: UTC
      - "BACKUP_AT_BOOT=true"                       # default: false
      - "BACKUP_KEEP_DAYS=30"                       # default: 7
      - "HEALTHCHECKS_URL=https://hc.example.com/ping/..."  # default: empty
```


## Docker tags and Postgresql versions

The first number in the Docker tag is the version of Postgresql; the last number is the version of docker-postgres-backup.  For example, the tag `13-alpine-1.0` indicates Postgresql version 13, docker-postgres-backup version 1.0.


## Configuration

### Volume ownership

On the host, the ownership of the `/backup` volume (`/srv/pgbackups` in the example above) must be `70:70`.

### Schedule

Backups run once a day.

If `BACKUP_AT_BOOT` is `true`, a backup will run when the container is started (i.e., for testing).

### Retention

Backups older than `BACKUP_KEEP_DAYS` are deleted.  (Set to `0` to keep forever.)

### Healthchecks support

Set `HEALTHCHECKS_URL` to your [https://healthchecks.io/](healthchecks) URL.


## License

```
Copyright 2021 John Begenisich

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
```
