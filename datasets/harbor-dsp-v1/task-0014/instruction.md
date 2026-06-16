# fix: surface all ExtractParams errors on APIServerReady status

## Summary

- Resolves follow-up to review on [opendatahub-io/data-science-pipelines-operator#1005](https://github.com/opendatahub-io/data-science-pipelines-operator/pull/1005#discussion_r3039673189) (only ErrManagedPipelinesImageUnset previously updated status; other ExtractParams errors requeued without surfacing the reason in status).

- Call setStatusAsNotReady for every ExtractParams failure, not only ErrManagedPipelinesImageUnset, so the DSPA APIServerReady condition shows why reconciliation is stuck (for example invalid volume limits, invalid RELATED_IMAGE_* env names, missing ConfigMap references).

- Add table-driven Reconcile tests that cover several real ExtractParams error paths and assert status + requeue behavior.


## Description of your changes

### Why APIServerReady for every ExtractParams failure:
We surface them on APIServerReady because that condition already represented this gate (including the earlier managed-pipelines image special case), the API server is the first workload that consumes these parameters, and we avoid adding a new condition type or updating downstream component conditions that never ran.

### controllers/dspipeline_controller.go
On any ExtractParams error: log the error, call setStatusAsNotReady for APIServerReady with FailingToDeploy and the error message, then return the same requeue result as before.

### controllers/apiserver_test.go

- Helper requireAPIServerReadyCondition to read the APIServerReady condition from status.
- TestReconcile_SetsAPIServerNotReadyOnExtractParamsErrors: table-driven cases for managed pipelines image unset, invalid RELATED_IMAGE_* env var name, invalid managed pipelines volumeSizeLimit, and missing custom KFP launcher ConfigMap.

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->

## Summary by CodeRabbit

* **Bug Fixes**
  * Improved error handling for parameter extraction during deployment, ensuring the API server status is consistently updated when configuration extraction fails, regardless of the specific error type.

* **Tests**
  * Expanded test coverage to validate API server status reporting across multiple parameter extraction failure scenarios.

<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Files involved
- `controllers/apiserver_test.go`
- `controllers/dspipeline_controller.go`
