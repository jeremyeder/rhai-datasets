FROM golang:latest
RUN apt-get update && apt-get install -y --no-install-recommends \
    git patch && rm -rf /var/lib/apt/lists/*
WORKDIR /testbed
RUN git clone https://github.com/opendatahub-io/data-science-pipelines-operator.git /testbed \
    && git checkout 6eb1e98b0b51addced7f882a3214894116881655
RUN mkdir -p /logs/verifier
