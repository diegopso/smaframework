import re, os, shutil, traceback, sys

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

import matplotlib
matplotlib.use('Agg')

import smaframework.filters.nyc_green_taxis as NycGreenTaxisFilter
import smaframework.filters.nyc_yellow_taxis as NycYellowTaxisFilter
import smaframework.extractor.csv as CsvDataExtractor
import smaframework.extractor.twitterstream as TwitterStream
import smaframework.organizer.magify as Magify
import smaframework.analyzer.bucketizer as Bucketizer
import smaframework.analyzer.fuzzymatcher as FuzzyMatcher
import smaframework.analyzer.magtools.heatmap as MagHeatmap
from smaframework.common.env import env

if __name__ == '__main__':
    # bounding box for filtering
    boundary = {
        'min_lat': 40.632,
        'max_lat': 40.849,
        'min_lon': -74.060,
        'max_lon': -73.762,
        'min_timestamp': 1456790399,
        'max_timestamp': 1459468800,
        }

    # filter dataset using bounding box
    NycYellowTaxisFilter.filter('examples/data/', 'yellow_taxis_test.csv', overwrite=False, **boundary)

    # move data to entries DB
    CsvDataExtractor.extract('examples/data/', 'data/entries/', 'yellow_taxis', [['id', 'tpep_pickup_datetime', 'pickup_latitude', 'pickup_longitude'],['id', 'tpep_dropoff_datetime', 'dropoff_latitude', 'dropoff_longitude']], file_regex=re.compile('^yellow_taxis_test-.*\.csv$'), datetime_format='%Y-%m-%d %H:%M:%S')
    CsvDataExtractor.extract('examples/data/', 'data/entries/', 'twitter', [['uid', 'timestamp', 'lon', 'lat']], file_regex=re.compile('^nyc_twitter_test\.csv$'), datetime_format='%Y-%m-%d %H:%M:%S')
    
    # organize entries in the MAG structure
    Magify.organize('data/entries/', 'default')
    
    # create indexes on data for fuzzymatcher run
    Bucketizer.bucketize('data/mag/nodes/', (40.849068, -74.060914, 1451606400), 200, 4*60*60)
    Bucketizer.index('data/buckets/', 200, 4*60*60, 'yellow_taxis', file_regex=re.compile('^[a-z0-9]+\.csv$'))
    Bucketizer.index('data/buckets/', 200, 4*60*60, 'twitter', file_regex=re.compile('^[a-f0-9]+\.csv$'))
    
    # create heatmaps from the data
    MagHeatmap.layer('twitter', env('GOOGLE_MAPS_KEY'), 'data/mag/nodes/')
    MagHeatmap.layer('yellow_taxis', env('GOOGLE_MAPS_KEY'), 'data/buckets/index/', buckets=True, file_regex=re.compile('^yellow_taxis-.*\.csv$'))
    
    # create a bucket frequency histogram
    Bucketizer.histogram('data/buckets/', ['twitter', 'yellow_taxis'], False, file_regex=re.compile('.*\.csv'))
    
    # evaluate the matches using Fuzzy Matcher and plot them and the persistent matches
    FuzzyMatcher.analyze('data/buckets/index/', 100, 2*60*60, 'twitter', 'yellow_taxis', file_regex=re.compile('^twitter.*\.csv$'))
    FuzzyMatcher.heatmap(env('GOOGLE_MAPS_KEY'), 'data/fuzzy-matches/', 'twitter')
    FuzzyMatcher.persistent_matches(env('GOOGLE_MAPS_KEY'), 'data/fuzzy-matches/', 'twitter', 'yellow_taxis')