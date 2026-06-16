FROM golang:latest
RUN apt-get update && apt-get install -y --no-install-recommends \
    git patch && rm -rf /var/lib/apt/lists/*
WORKDIR /testbed
RUN git clone https://github.com/opendatahub-io/data-science-pipelines-operator.git /testbed \
    && git checkout 649f68acb9fe5142bc9509cd98e73ea5a0669c4d
RUN mkdir -p /logs/verifier
