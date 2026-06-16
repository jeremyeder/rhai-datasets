 	assert.NotEmpty(t, params.APIServerConfigHash)
 }
 
func TestReconcileAPIServer_ConfigHashChangesWhenPlatformVersionChanges(t *testing.T) {
	t.Cleanup(func() { viper.Reset() })
	ctx := context.Background()

	dspa := testutil.CreateEmptyDSPA()
	dspa.Name = "dspa"
	dspa.Namespace = "ns"
	dspa.Spec.APIServer = &dspav1.APIServer{Deploy: true, EnableSamplePipeline: false}
	dspa.Spec.APIServer.ManagedPipelines = nil

	_, _, reconciler := CreateNewTestObjects()

	viper.Set("DSPO.PlatformVersion", "v1.0")
	params1 := &DSPAParams{}
	require.NoError(t, params1.ExtractParams(ctx, dspa, reconciler.Client, reconciler.Log))
	require.NoError(t, reconciler.ReconcileAPIServer(ctx, dspa, params1))

	viper.Set("DSPO.PlatformVersion", "v2.0")
	params2 := &DSPAParams{}
	require.NoError(t, params2.ExtractParams(ctx, dspa, reconciler.Client, reconciler.Log))
	require.NoError(t, reconciler.ReconcileAPIServer(ctx, dspa, params2))

	assert.NotEqual(t, params1.APIServerConfigHash, params2.APIServerConfigHash,
		"hash should differ when platform version changes")
}

 func TestExtractParams_ManagedPipelinesImageFromSpec(t *testing.T) {
 	t.Cleanup(func() { viper.Reset() })
 