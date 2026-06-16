 import (
 	"encoding/json"
 	"testing"
	"time"
 
	"github.com/go-logr/logr"
 	dspav1 "github.com/opendatahub-io/data-science-pipelines-operator/api/v1"
 	"github.com/opendatahub-io/data-science-pipelines-operator/controllers/testutil"
 	"github.com/stretchr/testify/assert"
 	require.Equal(t, *workspace.VolumeClaimTemplateSpec.VolumeMode, *unmarshalled["VolumeClaimTemplateSpec"].VolumeMode)
 	require.Equal(t, *workspace.VolumeClaimTemplateSpec.StorageClassName, *unmarshalled["VolumeClaimTemplateSpec"].StorageClassName)
 }

func TestSetupCompiledPipelineSpecPatch(t *testing.T) {
	tt := []struct {
		name           string
		params         DSPAParams
		expectedPatch  string
		expectedFields map[string]interface{}
	}{
		{
			name: "no ResourceTTL set - empty patch",
			params: DSPAParams{
				APIServer: &dspav1.APIServer{Deploy: true},
			},
			expectedPatch: "",
		},
		{
			name: "nil APIServer - empty patch",
			params: DSPAParams{
				APIServer: nil,
			},
			expectedPatch: "",
		},
		{
			name: "ResourceTTL set to 1h (3600s)",
			params: DSPAParams{
				APIServer: &dspav1.APIServer{
					Deploy:      true,
					ResourceTTL: &metav1.Duration{Duration: 1 * time.Hour},
				},
			},
			expectedFields: map[string]interface{}{
				"ttlStrategy": map[string]interface{}{
					"secondsAfterCompletion": float64(3600),
				},
			},
		},
		{
			name: "ResourceTTL set to 0s",
			params: DSPAParams{
				APIServer: &dspav1.APIServer{
					Deploy:      true,
					ResourceTTL: &metav1.Duration{Duration: 0},
				},
			},
			expectedFields: map[string]interface{}{
				"ttlStrategy": map[string]interface{}{
					"secondsAfterCompletion": float64(0),
				},
			},
		},
		{
			name: "ResourceTTL set to 24h (86400s)",
			params: DSPAParams{
				APIServer: &dspav1.APIServer{
					Deploy:      true,
					ResourceTTL: &metav1.Duration{Duration: 24 * time.Hour},
				},
			},
			expectedFields: map[string]interface{}{
				"ttlStrategy": map[string]interface{}{
					"secondsAfterCompletion": float64(86400),
				},
			},
		},
		{
			name: "ResourceTTL set to 30m (1800s)",
			params: DSPAParams{
				APIServer: &dspav1.APIServer{
					Deploy:      true,
					ResourceTTL: &metav1.Duration{Duration: 30 * time.Minute},
				},
			},
			expectedFields: map[string]interface{}{
				"ttlStrategy": map[string]interface{}{
					"secondsAfterCompletion": float64(1800),
				},
			},
		},
		{
			name: "ResourceTTL set to empty duration (zero value)",
			params: DSPAParams{
				APIServer: &dspav1.APIServer{
					Deploy:      true,
					ResourceTTL: &metav1.Duration{}, // empty/zero duration
				},
			},
			expectedFields: map[string]interface{}{
				"ttlStrategy": map[string]interface{}{
					"secondsAfterCompletion": float64(0),
				},
			},
		},
	}

	for _, tc := range tt {
		t.Run(tc.name, func(t *testing.T) {
			tc.params.SetupCompiledPipelineSpecPatch(logr.Discard())

			if tc.expectedPatch != "" {
				assert.Equal(t, tc.expectedPatch, tc.params.CompiledPipelineSpecPatch)
			} else if tc.expectedFields != nil {
				// Verify the JSON contains expected fields
				var actualFields map[string]interface{}
				err := json.Unmarshal([]byte(tc.params.CompiledPipelineSpecPatch), &actualFields)
				require.NoError(t, err)
				assert.Equal(t, tc.expectedFields, actualFields)
			} else {
				assert.Empty(t, tc.params.CompiledPipelineSpecPatch)
			}
		})
	}
}

func TestExtractParams_WithResourceTTL(t *testing.T) {
	ctx, params, client := CreateNewTestObjects()

	dspa := testutil.CreateDSPAWithResourceTTL(1 * time.Hour)

	err := params.ExtractParams(ctx, dspa, client.Client, client.Log)
	require.NoError(t, err)
	require.NotEmpty(t, params.CompiledPipelineSpecPatch)

	var patchFields map[string]interface{}
	err = json.Unmarshal([]byte(params.CompiledPipelineSpecPatch), &patchFields)
	require.NoError(t, err)

	ttlStrategy, ok := patchFields["ttlStrategy"].(map[string]interface{})
	require.True(t, ok, "ttlStrategy should be a map")

	secondsAfterCompletion, ok := ttlStrategy["secondsAfterCompletion"].(float64)
	require.True(t, ok, "secondsAfterCompletion should be a number")
	assert.Equal(t, float64(3600), secondsAfterCompletion)
}

func TestExtractParams_WithoutResourceTTL(t *testing.T) {
	ctx, params, client := CreateNewTestObjects()

	dspa := testutil.CreateEmptyDSPA()
	dspa.Spec.APIServer = &dspav1.APIServer{Deploy: true}
	dspa.Spec.PodToPodTLS = testutil.BoolPtr(false)

	err := params.ExtractParams(ctx, dspa, client.Client, client.Log)
	require.NoError(t, err)
	assert.Empty(t, params.CompiledPipelineSpecPatch)
}