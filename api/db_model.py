from mongoengine import *
connect('api')

class User(Document):
    userid = StringField(required=True)
    playground = ListField(StringField())
    pwd = StringField()

class PlaygroundLabeledMetadata(Document):
    userid = StringField(required=True)
    pgid = StringField(required=True) # share pgid with its associated playground
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
    new_srcid = ListField()
    playground_labeled_metadata = ListField(ReferenceField(PlaygroundLabeledMetadata))
    # playground_labeled_metadata_id = StringField()

class BaseLabeledMetadata(Document):
    # db_id = StringField(required=True)
    srcid = StringField(required=True)
    building = StringField(required=True)
    point_tagset = StringField(required=True)
    fullparsing = DictField()
    tagsets = ListField(StringField())
    tagsets_parsing = DictField() # optional

# class RawMetadata(Document)
#todo: update google doc