import sys
sys.path.append("..")
import json
import pdb

import pandas as pd
import numpy as np

from db_model import *
from plastering.common import *
# from plastering.helper import load_uva_building, load_ucb_building
# from plastering.helper import extract_raw_ucb_labels
# from plastering.rdf_wrapper import get_top_class
from jasonhelper import argparser

UCB_BUILDINGS = ['sdh', 'soda', 'ibm']
CMU_BUILDINGS = ['ghc']

# add labeled metadata
def parse_fullparsing(building, write_rawmetadata=False):
    with open('../groundtruth/{0}_full_parsing.json'.format(building), 'r') as fp:
        fullparsings = json.load(fp)
    for srcid, fullparsing in fullparsings.items():
        if building in UCB_BUILDINGS + CMU_BUILDINGS:
            fullparsing = {
                'VendorGivenName': fullparsing
            }
        point = LabeledMetadata.objects(srcid=srcid, building=building)\
                               .upsert_one(srcid=srcid, building=building)
        point.fullparsing = fullparsing
        point.save()
        if write_rawmetadata:
            rawpoint = RawMetadata.objects(srcid=srcid, building=building)\
                .upsert_one(srcid=srcid, building=building)
            sentence = ''.join([row[0] for row in fullparsing['VendorGivenName']])
            rawpoint.metadata = {
                'VendorGivenName': sentence
            }
            rawpoint.save()

    print('Finished adding full parsing')

# add tagsets
def parse_tagsets(building):
    with open('../groundtruth/{0}_tagsets.json'.format(building), 'r') as fp:
        true_tagsets = json.load(fp)
    for srcid, tagsets in true_tagsets.items():
        point = LabeledMetadata.objects(srcid=srcid, building=building)\
                               .upsert_one(srcid=srcid, building=building)
        point.tagsets = tagsets
        point_tagset = sel_point_tagset(tagsets)
        if not point_tagset:
            point_tagset = 'none'
        point.point_tagset = point_tagset
        point.save()

if __name__ == '__main__':
    argparser.add_argument('-b', type=str, dest='building', required=True)
    args = argparser.parse_args()
    building = args.building

    if building in CMU_BUILDINGS:
        parse_tagsets(building)
        parse_fullparsing(building, write_rawmetadata=True)