# predict_service.py
import falcon
from util.ctr.dsp.dsp_predict import OnlineService

class PredictService:
    def on_get(self, req, resp):
        """Handles GET requests"""
        data_list = req.get_param_as_list('data')
        predict = -1
        if data_list is not None and len(data_list) == 12:
            data = ','.join(data_list)
            dsp_predict = OnlineService.getInstance()
            predict = dsp_predict.predict(data)
        resp.status = falcon.HTTP_200  # This is the default status
        resp.body = (str(predict))


def load_weights():
    dsp_predict = OnlineService.getInstance()
    print('begin load weights')
    dsp_predict.load_w('data/dsp_model.csv')
    dsp_predict.load_learner(.1, .4, .08)
    print('end load weights')

# load weights
load_weights()

# falcon.API instances are callable WSGI apps
app = api = falcon.API()

# Resources are represented by long-lived class instances
predict_service = PredictService()

# things will handle all requests to the '/things' URL path
api.add_route('/predict_service', predict_service)
