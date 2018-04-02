import os, sys

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

import smaframework.analyzer.clustering.flow as FlowClusterer
from smaframework.common.env import env

if __name__ == '__main__':
    filename = 'examples/data/flow_test.csv'
    out_filename = 'data/results/flow_test'

    if not os.path.exists('data/'):
        os.makedirs('data/')

    if not os.path.exists('data/results/'):
        os.makedirs('data/results/')

    FlowClusterer.cluster_hdbscan(filename, ['origin_latitude', 'origin_longitude'], ['destination_latitude', 'destination_longitude'], output_file=out_filename, gmaps_key=env('GOOGLE_MAPS_KEY'), min_size=5)