# feat(controller): Add ResourceTTL configuration field for DSPAs

## Description of your changes:
Adds a new field, `resourceTTL` to the APIServer item in DSPA CRDs.  If set (not by default), DSPO will apply a workflow spec patch to all future execution of any PipelineRun which will clean up/delete resources such as Pods after n seconds, where n is the value provided to the resourceTTL field.

## Testing instructions
1. Deploy DSPO and basic DSPA
2. Check APIServer deployment
3. Verify no env var `COMPILED_PIPELINE_SPEC_PATCH` is present
4. edit DSPA with spec.apiServer.resourceTTL = 1234s
5. Verify APIServer redeploys and now has an env var `COMPILED_PIPELINES_SPEC_PATCH` with some simple JSON string and the ttl of 1234.
6. Update DSPA again and remove resourceTTL field
7. Verify APIServer redeploys and `COMPILED_PIPELINE_SPEC_PATCH` is no longer present again.

## Checklist
- [x] The commits are squashed in a cohesive manner and have meaningful messages.
- [x] Testing instructions have been added in the PR body (for PRs involving changes that are not immediately obvious).
- [x] The developer has manually tested the changes and verified that the changes work


<!-- This is an auto-generated comment: release notes by coderabbit.ai -->
## Summary by CodeRabbit

* **New Features**
  * Configurable Resource TTL for pipeline runs (CRD/API field) that applies a ttlStrategy to compiled pipeline specs and is exposed to the APIServer deployment when set.

* **Tests**
  * Added unit tests covering TTL-related patch generation and parameter extraction across varied durations.

* **Chores**
  * Consolidated test utilities (boolean-pointer helper) and updated tests to use the new helpers for consistency.

<sub>✏️ Tip: You can customize this high-level summary in your review settings.</sub>
<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Files involved
- `api/v1/dspipeline_types.go`
- `api/v1/zz_generated.deepcopy.go`
- `config/crd/bases/datasciencepipelinesapplications.opendatahub.io_datasciencepipelinesapplications.yaml`
- `config/internal/apiserver/default/deployment.yaml.tmpl`
- `controllers/apiserver_test.go`
- `controllers/dspipeline_params.go`
- `controllers/dspipeline_params_test.go`
- `controllers/mlmd_test.go`
- `controllers/testdata/declarative/case_2/deploy/cr.yaml`
- `controllers/testdata/declarative/case_2/expected/created/apiserver_deployment.yaml`
- `controllers/testutil/util.go`
- `controllers/workflow_controller_test.go`
