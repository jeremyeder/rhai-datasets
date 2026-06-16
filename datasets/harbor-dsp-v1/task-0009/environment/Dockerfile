FROM golang:latest
RUN apt-get update && apt-get install -y --no-install-recommends \
    git patch && rm -rf /var/lib/apt/lists/*
WORKDIR /testbed
RUN git clone https://github.com/opendatahub-io/data-science-pipelines-operator.git /testbed \
    && git checkout 13d6fd2e3f9ee4d12cc06bed72b2b035ddc4a6f5
RUN mkdir -p /logs/verifier
