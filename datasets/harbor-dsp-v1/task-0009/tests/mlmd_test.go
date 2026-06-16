 	v1 "github.com/openshift/api/route/v1"
 
 	dspav1 "github.com/opendatahub-io/data-science-pipelines-operator/api/v1"
	"github.com/opendatahub-io/data-science-pipelines-operator/controllers/testutil"
 	"github.com/stretchr/testify/assert"
 	"github.com/stretchr/testify/require"
 	appsv1 "k8s.io/api/apps/v1"
 	dspa := &dspav1.DataSciencePipelinesApplication{
 		Spec: dspav1.DSPASpec{
 			DSPVersion:  "v2",
			PodToPodTLS: testutil.BoolPtr(false),
 			APIServer:   &dspav1.APIServer{},
 			MLMD: &dspav1.MLMD{
 				Deploy: true,
 	dspa := &dspav1.DataSciencePipelinesApplication{
 		Spec: dspav1.DSPASpec{
 			DSPVersion:  "v2",
			PodToPodTLS: testutil.BoolPtr(false),
 			APIServer:   &dspav1.APIServer{},
 			MLMD: &dspav1.MLMD{
 				Deploy: false,
 	dspa := &dspav1.DataSciencePipelinesApplication{
 		Spec: dspav1.DSPASpec{
 			DSPVersion:  "v2",
			PodToPodTLS: testutil.BoolPtr(false),
 			APIServer:   &dspav1.APIServer{},
 			Database: &dspav1.Database{
 				DisableHealthCheck: false,
 	dspa := &dspav1.DataSciencePipelinesApplication{
 		Spec: dspav1.DSPASpec{
 			DSPVersion:  "v2",
			PodToPodTLS: testutil.BoolPtr(false),
 			APIServer:   &dspav1.APIServer{},
 			MLMD: &dspav1.MLMD{
 				Deploy: true,
 	dspa := &dspav1.DataSciencePipelinesApplication{
 		Spec: dspav1.DSPASpec{
 			DSPVersion:  "v2",
			PodToPodTLS: testutil.BoolPtr(false),
 			APIServer:   &dspav1.APIServer{},
 			MLMD: &dspav1.MLMD{
 				Deploy: true,
 	assert.Nil(t, err)
 }
 
 func TestGetEndpointsMLMD(t *testing.T) {
 	testNamespace := "testnamespace"
 	testDSPAName := "testdspa"
 	dspa := &dspav1.DataSciencePipelinesApplication{
 		Spec: dspav1.DSPASpec{
 			DSPVersion:  "v2",
			PodToPodTLS: testutil.BoolPtr(false),
 			APIServer:   &dspav1.APIServer{},
 			MLMD: &dspav1.MLMD{
 				Deploy: true,