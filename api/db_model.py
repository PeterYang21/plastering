from mongoengine import *
import sys
sys.path.append("..")
from plastering.metadata_interface import *
connect('plastering')

class PlaygroundLabeledMetadata(Document):
    userid = StringField(required=True) # optional ?
    pgid = StringField(required=True) # share pgid with its associated playground
    timestamp = DateTimeField() # record most recent version 
    srcid = StringField(required=True)
    building = StringField(required=True)
    point_tagset = StringField(required=True)
    fullparsing = DictField()
    tagsets = ListField(StringField())
    tagsets_parsing = DictField() # optional

class Playground(Document): 
    userid = StringField(required=True)
    pgid = StringField(required=True)
    building = StringField(required=True)
    algo_type = StringField(required=True)
    algo_model = BinaryField()
    new_srcid = ListField() # todo: use map to avoid duplicates
    playground_labeled_metadata = ListField(ReferenceField(PlaygroundLabeledMetadata))

class User(Document):
    userid = StringField(required=True)
    playground = ListField(ReferenceField(Playground))
    pwd = StringField(required=True)