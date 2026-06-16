FROM golang:latest
RUN apt-get update && apt-get install -y --no-install-recommends \
    git patch && rm -rf /var/lib/apt/lists/*
WORKDIR /testbed
RUN git clone https://github.com/opendatahub-io/data-science-pipelines-operator.git /testbed \
    && git checkout 1eec325246d8998cbec17a0f86ce093762d8905c
RUN mkdir -p /logs/verifier
