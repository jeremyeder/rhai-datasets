FROM golang:latest
RUN apt-get update && apt-get install -y --no-install-recommends \
    git patch && rm -rf /var/lib/apt/lists/*
WORKDIR /testbed
RUN git clone https://github.com/opendatahub-io/models-as-a-service.git /testbed \
    && git checkout a24c8c8
COPY solution.patch /tmp/solution.patch
RUN git apply --reverse /tmp/solution.patch && rm /tmp/solution.patch
RUN mkdir -p /logs/verifier
