 	"testing"
 
 	dspav1 "github.com/opendatahub-io/data-science-pipelines-operator/api/v1"
	"github.com/opendatahub-io/data-science-pipelines-operator/controllers/testutil"
 	"github.com/spf13/viper"
 	"github.com/stretchr/testify/assert"
 	appsv1 "k8s.io/api/apps/v1"
 	// Construct DSPASpec with deployed WorkflowController
 	dspa := &dspav1.DataSciencePipelinesApplication{
 		Spec: dspav1.DSPASpec{
			PodToPodTLS: testutil.BoolPtr(false),
 			APIServer:   &dspav1.APIServer{},
 			WorkflowController: &dspav1.WorkflowController{
 				Deploy: true,
 	// Construct DSPASpec with deployed WorkflowController
 	dspa := &dspav1.DataSciencePipelinesApplication{
 		Spec: dspav1.DSPASpec{
			PodToPodTLS: testutil.BoolPtr(false),
 			APIServer:   &dspav1.APIServer{},
 			WorkflowController: &dspav1.WorkflowController{
 				Deploy: true,
 	// Construct DSPASpec with deployed WorkflowController
 	dspa := &dspav1.DataSciencePipelinesApplication{
 		Spec: dspav1.DSPASpec{
			PodToPodTLS: testutil.BoolPtr(false),
 			APIServer:   &dspav1.APIServer{},
 			WorkflowController: &dspav1.WorkflowController{
 				Deploy: true,
 	// Construct DSPASpec with deployed WorkflowController
 	dspa := &dspav1.DataSciencePipelinesApplication{
 		Spec: dspav1.DSPASpec{
			PodToPodTLS: testutil.BoolPtr(false),
 			APIServer:   &dspav1.APIServer{},
 			WorkflowController: &dspav1.WorkflowController{
 				Deploy: true,