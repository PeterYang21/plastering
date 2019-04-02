from flask import Flask, request, session
from flask_restful import reqparse, abort, Api, Resource
import sys
sys.path.append("..")
from db_model import *
from db_helper import *
from algo_generator import *
import pickle, uuid

class Login(Resource):
    def post(self):
        """
        input: userID, password
        """
        userid, pwd = request.form['userid'], request.form['pwd']
        # todo: update based on single field rather than both
        user = User.objects(userid=userid)\
                   .upsert_one(userid=userid, pwd=pwd, playground=[])
        print(user.userid, user.pwd, user.playground)
        # user.playground = list()
        user.save() # playground is empty list by default

class BuildPlayground(Resource):
    def post(self):
        """
        initialize db of current playground and algorithm instance
        input: userid, algorithm, target building
        output: none
        """
        userid, building, algo_type = request.form['userid'], request.form['building'], request.form['algo_type']
        user = User.objects(userid=userid).first()
        pg = Playground.objects(
            userid=userid, 
            building=building, 
            algo_type=algo_type
        ).first()
        
        # assume new user, thus no previous playground record
        if not pg: 
            # algo_instance = get_algo_instance(algo_type=algo_type, target_building=building) # todo
            # algo_binaries = pickle.dumps(algo_instance, protocol=pickle.HIGHEST_PROTOCOL)
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
                # algo_model=algo_binaries,
                playground_labeled_metadata=pg_docs
            ).save()

            # add playground to user's record
            user.playground.append(pg)
            user.save()
            print('add playground:{} for user:{}'.format(pg.pgid, user.userid))

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
        pgid = request.form['pgid']
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
        pgid = request.form['pgid']
        srcid, building, expert_label = request.form['srcid'], request.form['building'], request.form['expert_label']
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
        pgid = request.form['pgid']
        obj = Playground.objects(pgid=pgid).first()
        model = pickle.loads(obj.algo_model)
        # update model with newly added srcids
        model.update_model(obj.new_srcid)
        algo_binaries = pickle.dumps(model, protocol=pickle.HIGHEST_PROTOCOL)
        obj.algo_model = model
        obj.save()

class Predict(Resource):
    pass