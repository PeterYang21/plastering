from flask import Flask, request, session, jsonify
from flask_restful import reqparse, abort, Api, Resource
import sys, uuid
sys.path.append("..")
from db_model import *
from utils import *
import dill as pickle
import logging
from datetime import datetime

app = Flask(__name__) 
logging.basicConfig(filename="api.log",  format='%(asctime)s %(message)s', filemode='a') 
logger = logging.getLogger()
logger.setLevel(logging.INFO)
app.secret_key = 'SECRET_KEY'
# todo: add session
# db.({session_key: {
#     user_id: 'USER_ID',
#     expiration_date: '2019=---',
#     building: 'ghc',
#     pgid: uuid,
# }})
@app.route('/login', methods=['POST'])
def login():
    """
    input: userID, password
    """
    userid, pwd = request.form['userid'], request.form['pwd']
    user = User.objects(userid=userid)\
            .upsert_one(userid=userid, pwd=pwd, playground=[]) # playground is empty list by default
    user.save() 
    print(logger)
    logger.info('userid={} logins'.format(userid))
    message = {'userid': userid}
    resp = jsonify(message)
    return resp

@app.route('/playground', methods=['POST'])
def build_playground():
    """
    build a playground based on user's input building and algorithm type
    input: userid, algorithm, target building
    output: none
    """
    userid, building, algo_type = request.form['userid'], request.form['building'], request.form['algo_type']
    user = User.objects(userid=userid).first()
    pgid = str(uuid.uuid4())
    algo_instance = get_algo_instance(algo_type=algo_type, target_building=building, pgid=pgid) 
    algo_binaries = pickle.dumps(algo_instance, protocol=pickle.HIGHEST_PROTOCOL)
    objs = RawMetadata.objects(building=building)
    pg = Playground(
        userid=userid,
        pgid=pgid,
        building=building,
        algo_type=algo_type,
        algo_model=algo_binaries,
        playground_labeled_metadata=[]
    ).save()

    # add playground to user's record
    user.playground.append(pg)
    user.save()
    logger.info('build playground={} for user={}'.format(pg.pgid, user.userid))

    message = {
        'userid': userid,
        'new playground': pgid
    }
    resp = jsonify(message)
    return resp

@app.route('/playground', methods=['GET']) # todo: need front-end (on-click) support
def get_playgrounds(userid):
    """
    display all playgrounds of current user
    input: none
    output: none
    """
    userid = request.form['userid']
    playgrounds = Playground.objects(userid=userid)
    pass

@app.route('/playground/<pgid>/select_example', methods=['GET'])
def select_example(pgid):
    """
    input: pgid
    output: most informative example that needs expert labeling
    """
    # load model from db
    obj = Playground.objects(pgid=pgid).first() 
    model = pickle.loads(obj.algo_model)

    # select informative example 
    new_sample_id = model.select_informative_samples(sample_num=1)[0]
    raw_point = RawMetadata.objects(srcid=new_sample_id).first()
    srcid, building, raw_metadata = raw_point['srcid'], raw_point['building'], raw_point['metadata']
    obj.new_srcid.append(srcid)
    obj.save()

    logger.info('select example from pgid={}, srcid={}, building={}, raw_metadata={}'.format(pgid, srcid, building, raw_metadata))
    message = {
        'srcid': srcid, 
        'building': building,
        'raw_metadata': raw_metadata
    }
    resp = jsonify(message)
    return resp

@app.route('/playground/<pgid>/labeled_metadata', methods=['POST'])
def insert_labeled_example(pgid): # todo: need front-end support to specify labels
    """
    input: srcid, building, annotated label
    """
    userid, srcid, expert_label = request.form['userid'], request.form['srcid'], request.form['expert_label']
    building = Playground.objects(pgid=pgid).first().building
    insert_label(
        userid=userid,
        pgid=pgid,
        building=building,
        srcid=srcid, # pgid + srcid act as primary key
        fullparsing=None,
        tagsets=None,
        point_tagset=expert_label # currently specific to Zodiac here
    )

    logger.info('userid={} inserts label {} for pgid={}, srcid={}, building={}'.format(userid, expert_label, pgid, srcid, building))
    message = {
        'fullparsing': None,
        'tagsets': None,
        'point_tagset': expert_label
    }
    resp = jsonify(message)
    return resp
    # todo: scrabble needs full parsing and tagsets ?
    # todo: need to know type of algorithm to decide function parameters 
    # todo: how to deal with new srcids after updating model? clear the new srcid list?

@app.route('/playground/<pgid>/update_model', methods=['GET'])
def update_model(pgid):
    """
    output: updated model statistics
    """
    # load model from db
    obj = Playground.objects(pgid=pgid).first()
    model = pickle.loads(obj.algo_model)

    # update model with newly added srcids
    model.update_model(obj.new_srcid)
    algo_binaries = pickle.dumps(model, protocol=pickle.HIGHEST_PROTOCOL)
    obj.algo_model = algo_binaries
    obj.save()
    return 'update model with srcid {}\n'.format(obj.new_srcid) # todo: accuracy is always 0

@app.route('/playground/<pgid>/predict', methods=['GET', 'POST'])
def predict(): # todo: predict all vs. predict points interested in 
    pass

if __name__ == '__main__':
    app.run(debug=True)
