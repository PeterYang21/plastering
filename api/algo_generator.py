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