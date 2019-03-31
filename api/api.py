from flask import Flask, request
from flask_restful import reqparse, abort, Api, Resource
import sys
sys.path.append("..")
from plastering.metadata_interface import *
from db_model import *
from db_helper import *
import pickle, uuid

class Login(Resource):
    def post(self):
        """
        input: userID
        """
        userid, pwd = request.forms['userid'], request.forms['pwd']
        user = User.objects(userid=userid, pwd=pwd)\
                   .upsert_one(userid=userid, pwd=pwd)
        if not user.playground:
            user.playground = []
        user.save()

class InitializePlayground(Resource):
    def post(self):
        """
        initialize db of current playground and algorithm instance
        input: userid, algorithm, target building
        output: none
        """
        userid, building, algo_type = request.forms['userid'], request.forms['building'], request.forms['algo_type']
        pg = Playground.objects(
            userid=userid, 
            building=building, 
            algo_type=algo_type
        )
        
        # assume new user, thus no previous playground record
        if not pg: 
            algo_model = get_algo_instance(algo_type=algo_type, building=building) # todo
            algo_binaries = pickle.dumps(algo_model, protocol=pickle.HIGHEST_PROTOCOL)
            objs = BaseLabeledMetadata.objects(building=building) # copy necessary data
            pg_docs = []
            for obj in objs:
                pgid = str(uuid.uuid4())
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
                
            Playground(
                userid=userid,
                pgid=pgid,
                building=building,
                algo_type=algo_type,
                algo_model=algo_binaries,
                playground_labeled_metadata=pg_docs
            ).save()

        # algo = Zodiac()
        # pickled = pickle(algo)
        # db.store(session_id, pickeled) # get algorithm object based on sessionID

class SelectExample(Resource):
    def get(self):
        """
        input: pgid
        output: most informative example that needs expert labeling
        """
        # load model from db
        pgid = request.forms['pgid']
        obj = Playground.objects(pgid=pgid).first()
        model = pickle.loads(obj.algo_model)

        # select example 
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

        return response
       
class InsertLabeledExample(Resource):
    def post(self):
        """
        input: srcid, building, annotated label
        """
        pgid = request.forms['pgid']
        srcid, building, expert_label = request.forms['srcid'], request.forms['building'], request.forms['expert_label']
        insert_label(
            pgid=pgid,
            srcid=srcid,
            building=building,
            point_tagset=expert_label
        )
        # todo: need to know type of algorithm to decide function parameters ?
        # todo: how to deal with new srcids after updating model? clear the new srcid list?

class UpdateModel(Resource):
    def get(self):
        """
        output: updated model statistics
        """
        # load model from db
        pgid = request.forms['pgid']
        obj = Playground.objects(pgid=pgid).first()
        model = pickle.loads(obj.algo_model)
        # update model with newly added srcids
        model.update_model(obj.new_srcid)
        algo_binaries = pickle.dumps(model, protocol=pickle.HIGHEST_PROTOCOL)
        obj.algo_model = model
        obj.save()

class Predict(Resource):
    pass

# get user algo from database in each api