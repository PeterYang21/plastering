from plastering.inferencers.zodiac import ZodiacInterface
from db_model import *

config = {
    'brick_version': '1.0.2',
    'brick_file': '/Users/yimingyang/Desktop/Project/plaster/plastering/brick/Brick_1_0_2.ttl',
    'brickframe_file': '/Users/yimingyang/Desktop/Project/plaster/plastering/brick/BrickFrame_1_0_2.ttl',
}

def get_algo_instance(algo_type, target_building):
    # Select labeled srcids (Not all the data are labeled yet.)
    labeled_list = LabeledMetadata.objects(building=target_building)
    target_srcids = [labeled['srcid'] for labeled in labeled_list]
    if algo_type == 'Zodiac':
        algo_instance = ZodiacInterface(
            target_building=target_building,
            target_srcids=target_srcids,
            config=config
        )
    
    return algo_instance

def insert_label(**params):
    pg_metadata = PlaygroundLabeledMetadata.objects(
        pgid=params['pgid'],
        srcid=params['srcid']    
    ).first()
    fullparsing, tagsets, point_tagset = params['fullparsing'], params['tagsets'], params['point_tagset']
    new_labels = {}
    if fullparsing:
        new_labels['set__fullparsing'] = fullparsing
    if point_tagset:
        new_labels['set__point_tagset'] = point_tagset
    if tagsets:
        new_labels['set__tagsets'] = tagsets
    print("new labels: ", new_labels)
    pg_metadata.update(**new_labels, upsert=True)
    pg_metadata.save()

def insert_groundtruth(srcid, building,
                       fullparsing=None, tagsets=None, point_tagset=None):
    obj = LabeledMetadata.objects(srcid=srcid)\
        .upsert_one(srcid=srcid, building=building)
    assert fullparsing or tagsets or point_tagset, 'WARNING:empty labels given'
    new_labels = {}
    if fullparsing:
        new_labels['set__fullparsing'] = fullparsing
    if point_tagset:
        new_labels['set__point_tagset'] = point_tagset
    if tagsets:
        new_labels['set__tagsets'] = tagsets
    print("new labels: ", new_labels)
    obj.update(**new_labels, upsert=True)
    obj.save()