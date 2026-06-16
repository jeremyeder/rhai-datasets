#!/bin/bash
mkdir -p /logs/verifier
cd /testbed
go test -v -count=1 ./controllers/... 2>&1 | tee /logs/verifier/test-stdout.txt
if [ ${PIPESTATUS[0]} -eq 0 ]; then echo 1 > /logs/verifier/reward.txt; else echo 0 > /logs/verifier/reward.txt; fi
exit 0
