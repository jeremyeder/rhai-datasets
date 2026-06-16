 	"testing"
 
 	"github.com/opendatahub-io/data-science-pipelines-operator/controllers/config"
	"github.com/opendatahub-io/data-science-pipelines-operator/controllers/testutil"
 
 	dspav1 "github.com/opendatahub-io/data-science-pipelines-operator/api/v1"
 	"github.com/stretchr/testify/assert"
 	// Construct DSPASpec with deployed APIServer
 	dspa := &dspav1.DataSciencePipelinesApplication{
 		Spec: dspav1.DSPASpec{
			PodToPodTLS: testutil.BoolPtr(false),
 			APIServer: &dspav1.APIServer{
 				Deploy: true,
 			},
 	// Construct DSPASpec with deployed APIServer
 	dspa := &dspav1.DataSciencePipelinesApplication{
 		Spec: dspav1.DSPASpec{
			PodToPodTLS: testutil.BoolPtr(false),
 			APIServer: &dspav1.APIServer{
 				Deploy: true,
 			},