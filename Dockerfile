# Stage 1: Build
FROM python:3.13-slim AS builder

ARG LOGLEVEL
ARG IMAP_SERVER
ARG IMAP_PORT
ARG USERNAME
ARG PASSWORD
ARG MAILBOX
ARG SAVE_DIR

ENV LOGLEVEL=$LOGLEVEL
ENV IMAP_SERVER=$IMAP_SERVER
ENV IMAP_PORT=$IMAP_PORT
ENV USERNAME=$USERNAME
ENV PASSWORD=$PASSWORD
ENV MAILBOX=$MAILBOX
ENV SAVE_DIR=$SAVE_DIR

WORKDIR /app

COPY requirements.txt .
RUN ./venv/bin/python -m pip install --no-cache-dir -U -r requirements.txt && \
    find /app/venv \( -type d -a -name test -o -name tests \) -o \( -type f -a -name '*.pyc' -o -name '*.pyo' \) -exec rm -rf '{}' \+

COPY dist/*.whl .
RUN ./venv/bin/python -m pip install --no-cache-dir *.whl && \
    rm -f *.whl && \
    find /app/venv \( -type d -a -name test -o -name tests \) -o \( -type f -a -name '*.pyc' -o -name '*.pyo' \) -exec rm -rf '{}' \+

CMD ["/app/venv/bin/python", "-m" , "imapsync"]
