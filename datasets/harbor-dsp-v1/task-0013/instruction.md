# Include `PlatformVersion` in API Server config hash and add unit test

## The issue resolved by this Pull Request:
Resolves https://redhat.atlassian.net/browse/RHOAIENG-51651
This is a follow-up of:
- https://github.com/opendatahub-io/data-science-pipelines-operator/pull/993

## Description of your changes:
<!--- This PR will be merged by any repository approver when it meets all the points in the checklist -->
<!--- Go over all the following points, and put an `x` in all the boxes that apply. -->
When `DSPO.PlatformVersion` changes (e.g. during a platform upgrade), the API server config hash did not change, so the API server pod was not rolled. This was only a problem when `ManagedPipelines` is nil and `EnableSamplePipeline` is false, because in that case `sampleConfigJSON` is a fixed string that doesn't embed the version.

This PR adds `params.PlatformVersion` to `combinedConfigHashInput` so that any platform version change triggers a pod rollout.

## Testing instructions
<!--- Add any information that testers/qe should be aware of when testing this PR. Examples include what components
to focus on, or what features are likely to be affected. -->
A unit test was added.

## Checklist
- [x] The commits are squashed in a cohesive manner and have meaningful messages.
- [x] Testing instructions have been added in the PR body (for PRs involving changes that are not immediately obvious).
- [x] The developer has manually tested the changes and verified that the changes work


<!-- This is an auto-generated comment: release notes by coderabbit.ai -->
## Summary by CodeRabbit

* **Bug Fixes**
  * Config hash now unconditionally includes platform version, so pod-template identities update reliably when platform version or related config changes.

* **Tests**
  * Added a test to verify configuration hashes change when the platform version is updated.

* **Manifests**
  * Updated expected pod template config-hash annotations in test fixtures to align with the new hashing behavior.
<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Files involved
- `controllers/apiserver.go`
- `controllers/apiserver_test.go`
- `controllers/testdata/declarative/case_0/expected/created/apiserver_deployment.yaml`
- `controllers/testdata/declarative/case_2/expected/created/apiserver_deployment.yaml`
- `controllers/testdata/declarative/case_3/expected/created/apiserver_deployment.yaml`
- `controllers/testdata/declarative/case_4/expected/created/apiserver_deployment.yaml`
- `controllers/testdata/declarative/case_5/expected/created/apiserver_deployment.yaml`
- `controllers/testdata/declarative/case_6/expected/created/apiserver_deployment.yaml`
- `controllers/testdata/declarative/case_8/expected/created/apiserver_deployment.yaml`
