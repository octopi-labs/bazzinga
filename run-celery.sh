#!/bin/bash

BASEDIR=$(dirname $(readlink -f $0))
VENV=venv/bin/activate

LOGS=/logs/

LIBCONFIG=/libapp/config/libconf.py
CELCONFIG=/libapp/config/celconf.py

LIBAPP=libapp
CELERY=tasks.celeryd

# Get Queue
QUEUE=celery
# Read each line from config file located at $BASEDIR$LIBCONFIG
while IFS='' read -r line || [[ -n "$line" ]]; do
    # Read current line and split string into
    IFS='=' read -a array <<< "$line"
    # Trim queue identifier
    Q_TYPE="$(echo -e "${array[0]}" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"
    if [ "${Q_TYPE}" == "EMAIL_Q" ]; then
        QUEUE="$(echo -e "${array[1]}" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"
        # Remove leading and trailing double quotes
        QUEUE="$(echo -e "${QUEUE}" | sed -e 's/^[[\"]]*//' -e 's/[[\"]]*$//')"
    fi
done < $BASEDIR$LIBCONFIG


# Get Celery configurations
LOGLEVEL=info
CONCURRENCY=1
LOGFILE=celery.log
while IFS='' read -r line || [[ -n "$line" ]]; do
    IFS='=' read -a array <<< "$line"
    CONFIG_VAL="$(echo -e "${array[0]}" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"

    # Get log level
    if [ "${CONFIG_VAL}" == "CELERY_LOG_LEVEL" ]; then
        LOGLEVEL="$(echo -e "${array[1]}" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"
        # Remove leading and trailing double quotes
        LOGLEVEL="$(echo -e "${LOGLEVEL}" | sed -e 's/^[[\"]]*//' -e 's/[[\"]]*$//')"
    fi
    # Get concurrency
    if [ "${CONFIG_VAL}" == "CELERY_CONCURRENCY" ]; then
        CONCURRENCY="$(echo -e "${array[1]}" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"
        # Remove leading and trailing double quotes
        CONCURRENCY="$(echo -e "${CONCURRENCY}" | sed -e 's/^[[\"]]*//' -e 's/[[\"]]*$//')"
    fi
    # Get log file
    if [ "${CONFIG_VAL}" == "CELERY_LOG_FILE" ]; then
        LOGFILE="$(echo -e "${array[1]}" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"
        # Remove leading and trailing double quotes
        LOGFILE="$(echo -e "${LOGFILE}" | sed -e 's/^[[\"]]*//' -e 's/[[\"]]*$//')"
    fi
done < $BASEDIR$CELCONFIG

# Activate virtual environment
cd $BASEDIR
source $VENV
# Run celery
celery -E -A $LIBAPP.$CELERY worker -Q $QUEUE --beat --concurrency=$CONCURRENCY --loglevel=$LOGLEVEL --logfile=$BASEDIR$LOGS$LOGFILE