 	dsPipelineAPIServerContainerName  = "ds-pipeline-api-server"
 )
 
func requireDSPAStatusCondition(t *testing.T, dspa *dspav1.DataSciencePipelinesApplication, conditionType string) metav1.Condition {
	t.Helper()
	for i := range dspa.Status.Conditions {
		if dspa.Status.Conditions[i].Type == conditionType {
			return dspa.Status.Conditions[i]
		}
	}
	t.Fatalf("expected condition type %q in status", conditionType)
	return metav1.Condition{}
}

 // getInitManagedPipelinesContainer returns the init-managed-pipelines container from the deployment, or nil if not found.
 func getInitManagedPipelinesContainer(t testing.TB, deployment *appsv1.Deployment) *corev1.Container {
 	t.Helper()
 	require.Contains(t, err.Error(), "IMAGES_PIPELINES_COMPONENTS")
 }
 
func TestReconcile_SetsAPIServerNotReadyOnExtractParamsErrors(t *testing.T) {
	tests := []struct {
		name            string
		prepareDSPA     func(t *testing.T) *dspav1.DataSciencePipelinesApplication
		wantMsgContains []string
	}{
		{
			name: "managed_pipelines_image_unset",
			prepareDSPA: func(_ *testing.T) *dspav1.DataSciencePipelinesApplication {
				d := testutil.CreateDSPAWithManagedPipelines("", nil, nil)
				d.Name = "dspa-mp-status"
				d.Namespace = "testnamespace"
				return d
			},
			wantMsgContains: []string{"managedPipelines", "Images.PipelinesComponents", "IMAGES_PIPELINES_COMPONENTS"},
		},
		{
			name: "invalid_related_image_env_var_name",
			prepareDSPA: func(t *testing.T) *dspav1.DataSciencePipelinesApplication {
				t.Setenv("RELATED_IMAGE_toolbox", "registry.example/x:latest")
				d := testutil.CreateDSPAWithManagedPipelines("img:latest", nil, nil)
				d.Name = "dspa-extract-bad-related"
				d.Namespace = "testnamespace"
				return d
			},
			wantMsgContains: []string{"invalid RELATED_IMAGE_* env var name"},
		},
		{
			name: "invalid_managed_pipelines_volume_size_limit",
			prepareDSPA: func(_ *testing.T) *dspav1.DataSciencePipelinesApplication {
				d := testutil.CreateDSPAWithManagedPipelines("img:latest", nil, nil)
				d.Spec.APIServer.ManagedPipelines.VolumeSizeLimit = "not-a-quantity"
				d.Name = "dspa-extract-volume"
				d.Namespace = "testnamespace"
				return d
			},
			wantMsgContains: []string{"managedPipelines.volumeSizeLimit must be a valid Kubernetes quantity"},
		},
		{
			name: "custom_kfp_launcher_configmap_not_found",
			prepareDSPA: func(_ *testing.T) *dspav1.DataSciencePipelinesApplication {
				d := testutil.CreateDSPAWithCustomKfpLauncherConfigMap("missing-launcher-cm")
				d.Name = "dspa-extract-launcher-cm"
				d.Namespace = "testnamespace"
				return d
			},
			wantMsgContains: []string{`configmaps "missing-launcher-cm"`, "not found"},
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			t.Cleanup(viper.Reset)
			viper.Reset()
			clearRelatedImageEnv(t)
 
			dspa := tt.prepareDSPA(t)
			ctx, _, reconciler := CreateNewTestObjects()
			require.NoError(t, reconciler.Client.Create(ctx, dspa))
 
			result, err := reconciler.Reconcile(ctx, ctrl.Request{
				NamespacedName: types.NamespacedName{Name: dspa.Name, Namespace: dspa.Namespace},
			})
			require.NoError(t, err)
			assert.True(t, result.Requeue, "should requeue when ExtractParams fails")
			wantRequeueAfter := config.GetDurationConfigWithDefault(config.RequeueTimeConfigName, config.DefaultRequeueTime)
			assert.Equal(t, wantRequeueAfter, result.RequeueAfter, "RequeueAfter should match configured value")

			updated := &dspav1.DataSciencePipelinesApplication{}
			require.NoError(t, reconciler.Get(ctx, types.NamespacedName{Name: dspa.Name, Namespace: dspa.Namespace}, updated))

			apiCond := requireDSPAStatusCondition(t, updated, config.APIServerReady)
			assert.Equal(t, metav1.ConditionFalse, apiCond.Status)
			assert.Equal(t, config.FailingToDeploy, apiCond.Reason)
			for _, sub := range tt.wantMsgContains {
				assert.Contains(t, apiCond.Message, sub)
			}
 
			crCond := requireDSPAStatusCondition(t, updated, config.CrReady)
			assert.Equal(t, metav1.ConditionFalse, crCond.Status)
			assert.Equal(t, config.FailingToDeploy, crCond.Reason)
			for _, sub := range tt.wantMsgContains {
				assert.Contains(t, crCond.Message, sub)
			}
		})
 	}
 }
 
 func TestDeployAPIServerWithManagedPipelines_OmittedImageUsesOperatorConfigDefault(t *testing.T) {