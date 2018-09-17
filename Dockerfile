FROM python:3.6-alpine

# Consume build args and set env vars
ARG ACCESS_KEY_ID
ARG ACCESS_KEY
ARG QUEUE_URL
ARG REGION

ENV ACCESS_KEY_ID ${ACCESS_KEY_ID}
ENV ACCESS_KEY ${ACCESS_KEY}
ENV QUEUE_URL ${QUEUE_URL}
ENV REGION ${REGION}

# Copy files dir to container
RUN mkdir -p /opt/sqs-cue
WORKDIR /opt/sqs-cue
COPY ./requirements.txt /opt/sqs-cue
COPY ./sqs_cue /opt/sqs-cue/sqs_cue

# Install python dependencies
RUN pip install -r requirements.txt
