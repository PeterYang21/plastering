from mongoengine import *
connect('api')

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

class LabeledMetadata(Document):
    srcid = StringField(required=True)
    building = StringField(required=True)
    point_tagset = StringField(required=True)
    fullparsing = DictField()
    tagsets = ListField(StringField())
    tagsets_parsing = DictField() # optional

class RawMetadata(Document):
    srcid = StringField(required=True)
    building = StringField(required=True)
    metadata = DictField()

class User(Document):
    userid = StringField(required=True)
    playground = ListField(ReferenceField(Playground))
    pwd = StringField(required=True)

#todo: update google doc