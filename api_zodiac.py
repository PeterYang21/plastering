from flask import Flask, request
from flask_restful import reqparse, abort, Api, Resource
from plastering.inferencers.zodiac import ZodiacInterface
from plastering.metadata_interface import *

# todo: place api in directory
class ExampleSelection(Resource):
    def get(self):
        """
        input: algorithm, target building 
        
        """
        algo_type = request['algoritm']
        session_id = session['id']

        user_algo = DataBase.get(session_id)[algo_type]
        user_algo.select_informative_samples()

        new_sample_id = zodiac.select_informative_samples(sample_num=1)[0]
        raw_point = RawMetadata.objects(srcid=new_sample_id).first()
        srcid, buidling, raw_metadata = raw_point['srcid'], raw_point['building'], raw_point['metadata']
        ret = {
            'srcid': srcid, 
            'building': buidling,
            'raw_metadata': raw_metadata
            }

        return ret
    
class PostExample(Resource):
    def post(self):
        args = parser.parse_args()
        srcid, building, expert_label = args['srcid'], args['building'], args['expert_label']
        insert_groundtruth(srcid, building, point_tagset=expert_label)
class UpdateModel(Resource):
    def post(self):
        zodiac.update_model([srcid]) # add new srcid to training set, prompt for required labels if needed 
        zodiac.learn_model() # learn after update

app = Flask(__name__)
api = Api(app)

target_building = 'ghc'
# target_building = 'uva_cse'
config = {
    'brick_version': '1.0.2',
    'brick_file': '/Users/yimingyang/Desktop/Project/plaster/plastering/brick/Brick_1_0_2.ttl',
    'brickframe_file': '/Users/yimingyang/Desktop/Project/plaster/plastering/brick/BrickFrame_1_0_2.ttl',
}

# Select labeled srcids (Not all the data are labeled yet.)
labeled_list = LabeledMetadata.objects(building=target_building)
target_srcids = [labeled['srcid'] for labeled in labeled_list]

zodiac = ZodiacInterface(target_building=target_building,
                         target_srcids=target_srcids,
                         config=config,
                         )

parser = reqparse.RequestParser()
parser.add_argument('srcid')
parser.add_argument('building')
parser.add_argument('expert_label')

zodiac.learn_model()
api.add_resource(ExampleSelection, '/selectexample') #####
api.add_resource(PostExample, '/postexample') #####
app.run(debug=True)
# todo: pred = zodiac.predict()
