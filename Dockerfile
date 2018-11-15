FROM python:3.6-alpine

# Consume build args and set env vars
ARG QUEUE_CONFIG_FILE
ENV QUEUE_CONFIG_FILE ${QUEUE_CONFIG_FILE}

# Copy files dir to container
RUN mkdir -p /opt/sqs-cue
WORKDIR /opt/sqs-cue
COPY ${QUEUE_CONFIG_FILE} /opt/sqs-cue/
COPY ./requirements.txt /opt/sqs-cue
COPY ./sqs_cue /opt/sqs-cue/sqs_cue

# Install python dependencies
RUN pip install -r requirements.txt
