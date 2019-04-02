from flask import Flask, request, session, jsonify
from flask_restful import reqparse, abort, Api, Resource
import sys
sys.path.append("..")
from db_model import *
from utils import *
import dill as pickle

app = Flask('api')

@app.route('/login', methods=['POST'])
def login():
    """
    input: userID, password
    """
    userid, pwd = request.form['userid'], request.form['pwd']
    # todo: update based on single field rather than both
    user = User.objects(userid=userid)\
            .upsert_one(userid=userid, pwd=pwd, playground=[])
    user.save() # playground is empty list by default
    
    return '{} login\n'.format(user.userid)

@app.route('/build_playground', methods=['GET', 'POST'])
def build_playground():
    """
    initialize db of current playground and algorithm instance
    input: userid, algorithm, target building
    output: none
    """
    if request.method == 'POST':
        userid, building, algo_type = request.form['userid'], request.form['building'], request.form['algo_type']
        user = User.objects(userid=userid).first()
        pg = Playground.objects(
            userid=userid, 
            building=building, 
            algo_type=algo_type
        ).first()
        
        # assume new user, thus no previous playground record
        if not pg: 
            algo_instance = get_algo_instance(algo_type=algo_type, target_building=building) # todo
            algo_binaries = pickle.dumps(algo_instance, protocol=pickle.HIGHEST_PROTOCOL)
            objs = LabeledMetadata.objects(building=building) # copy necessary data
            pg_docs = []
            pgid = str(uuid.uuid4())
            for obj in objs:
                pg_doc = PlaygroundLabeledMetadata(
                            userid=userid,
                            pgid=pgid,
                            srcid=obj.srcid,
                            building=building,
                            point_tagset=obj.point_tagset,
                            fullparsing=obj.fullparsing,
                            tagsets=obj.tagsets
                        ).save()
                pg_docs.append(pg_doc)
            print('finish copying {} objects from base labeled metadata'.format(len(pg_docs)))
                
            pg = Playground(
                userid=userid,
                pgid=pgid,
                building=building,
                algo_type=algo_type,
                algo_model=algo_binaries,
                playground_labeled_metadata=pg_docs
            ).save()

            # add playground to user's record
            user.playground.append(pg)
            user.save()
            print('add playground:{} for user:{}'.format(pg.pgid, user.userid))
    
    return 'build playground\n'

@app.route('/select_example', methods=['GET'])
def select_example():
    """
    input: pgid
    output: most informative example that needs expert labeling
    """
    # load model from db
    pgid = request.form['pgid']
    obj = Playground.objects(pgid=pgid).first() 
    model = pickle.loads(obj.algo_model)

    # select informative example 
    new_sample_id = model.select_informative_samples(sample_num=1)[0]
    raw_point = RawMetadata.objects(srcid=new_sample_id).first()
    srcid, buidling, raw_metadata = raw_point['srcid'], raw_point['building'], raw_point['metadata']
    response = {
        'srcid': srcid, 
        'building': buidling,
        'raw_metadata': raw_metadata
    }
    obj.new_srcid.append(srcid)
    obj.save()

    return jsonify(response)

@app.route('/insert_labeled_example', methods=['POST'])
def insert_labeled_example():
    """
    input: srcid, building, annotated label
    """
    # userid = request.form['userid']
    pgid = request.form['pgid']
    srcid, expert_label = request.form['srcid'], request.form['expert_label']
    insert_label(
        pgid=pgid,
        srcid=srcid, # pgid + srcid act as primary key
        fullparsing=None,
        tagsets=None,
        point_tagset=expert_label # currently specific to Zodiac here
    )
    return 'add label for srcid:{}\n'.format(srcid) 
    # todo: scrabble needs full parsing and tagsets ?
    # todo: need to know type of algorithm to decide function parameters ?
    # todo: how to deal with new srcids after updating model? clear the new srcid list?

@app.route('/update_model', methods=['GET'])
def update_model():
    """
    output: updated model statistics
    """
    # load model from db
    pgid = request.form['pgid']
    obj = Playground.objects(pgid=pgid).first()
    model = pickle.loads(obj.algo_model)
    # update model with newly added srcids
    model.update_model(obj.new_srcid)
    algo_binaries = pickle.dumps(model, protocol=pickle.HIGHEST_PROTOCOL)
    obj.algo_model = algo_binaries
    obj.save()
    return 'update model with srcid {}\n'.format(obj.new_srcid) # todo: accuracy is always 0

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    pass

if __name__ == '__main__':
    app.run(debug=True)
