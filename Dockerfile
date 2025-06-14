FROM python:3.13-slim

RUN apt update && apt install -y g++ ca-certificates && update-ca-certificates

WORKDIR /app

COPY requirements.txt .
RUN python -m pip install --no-cache-dir -U -r requirements.txt

COPY dist/*.whl .
RUN python -m pip install --no-cache-dir *.whl && \
    rm -f *.whl

ARG LOGLEVEL
ARG SYNC_PERIOD
ARG IMAP_LIST__0__LABEL
ARG IMAP_LIST__0__IMAP_SERVER
ARG IMAP_LIST__0__IMAP_PORT
ARG IMAP_LIST__0__USERNAME
ARG IMAP_LIST__0__PASSWORD
ARG IMAP_LIST__0__MAILBOX
ARG IMAP_LIST__1__LABEL
ARG IMAP_LIST__1__IMAP_SERVER
ARG IMAP_LIST__1__IMAP_PORT
ARG IMAP_LIST__1__USERNAME
ARG IMAP_LIST__1__PASSWORD
ARG IMAP_LIST__1__MAILBOX

ENV LOGLEVEL=$LOGLEVEL
ENV SAVE_DIR=/emails
ENV SYNC_PERIOD=$SYNC_PERIOD
ENV IMAP_LIST__0__LABEL=$IMAP_LIST__0__LABEL
ENV IMAP_LIST__0__IMAP_SERVER=$IMAP_LIST__0__IMAP_SERVER
ENV IMAP_LIST__0__IMAP_PORT=$IMAP_LIST__0__IMAP_PORT
ENV IMAP_LIST__0__USERNAME=$IMAP_LIST__0__USERNAME
ENV IMAP_LIST__0__PASSWORD=$IMAP_LIST__0__PASSWORD
ENV IMAP_LIST__0__MAILBOX=$IMAP_LIST__0__MAILBOX
ENV IMAP_LIST__1__LABEL=$IMAP_LIST__1__LABEL
ENV IMAP_LIST__1__IMAP_SERVER=$IMAP_LIST__1__IMAP_SERVER
ENV IMAP_LIST__1__IMAP_PORT=$IMAP_LIST__1__IMAP_PORT
ENV IMAP_LIST__1__USERNAME=$IMAP_LIST__1__USERNAME
ENV IMAP_LIST__1__PASSWORD=$IMAP_LIST__1__PASSWORD
ENV IMAP_LIST__1__MAILBOX=$IMAP_LIST__1__MAILBOX

CMD ["python", "-m" , "imapsync"]
