ARG PGVERSION
FROM postgres:$PGVERSION-alpine

RUN set -x \
	&& apk add --no-cache ca-certificates python3 py-pip

RUN pip install apscheduler

ENV BACKUP_PATH /backups
VOLUME /backups

COPY ./entrypoint.sh /entrypoint.sh
COPY ./pgbackup.py /pgbackup.py
RUN chmod +x /entrypoint.sh /pgbackup.py

USER postgres

ENTRYPOINT ["/entrypoint.sh"]
