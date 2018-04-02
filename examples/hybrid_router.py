import json, timeit, haversine, os, sys
from datetime import datetime
from functools import partial

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from smaframework.analyzer.hybrid_multimodal_router.model import perceived_time, perceived_score
import smaframework.extractor.google.directions as GoogleDirectionsExtractor
import smaframework.analyzer.hybrid_multimodal_router.router as HybridMultimodalRouter
from smaframework.common.env import env

if __name__ == '__main__':
    # creating function to evaluate score of routes
    score_function = partial(perceived_score, 0.5)

    # sample start and end points
    origin = (40.671748, -74.010330)
    destination = (40.709828, -73.962403)

    # get basis drivin way
    driving_ways = GoogleDirectionsExtractor.extract(env('GOOGLE_MAPS_KEY'), [origin], [destination], [datetime.now()], 'driving', {}, alternatives='true', layer='trips')
    
    # check traffic conditions for driving way
    driving_ways = HybridMultimodalRouter.analyse_ways(env('HERE_APP_ID'), env('HERE_APP_CODE'), driving_ways)
    
    # merge congested and free segments
    driving_ways = HybridMultimodalRouter.merge_segments(driving_ways)

    # get hybrid route availbale options
    trips = HybridMultimodalRouter.get_available_options(env(), driving_ways, score_function=score_function)

    # evaluate options based on different functions
    time_based = []
    price_based = []
    perceived_time_based = []
    perceived_score_based = []
    for t in trips:
        time_based.append(HybridMultimodalRouter.choose(t, lambda i, s: s['duration']))
        price_based.append(HybridMultimodalRouter.choose(t, lambda i, s: s['price']))
        perceived_time_based.append(HybridMultimodalRouter.choose(t, perceived_time))
        perceived_score_based.append(HybridMultimodalRouter.choose(t, score_function))

    # save results
    with open('data/results/selected_routes.json', 'w+') as f:
        json.dump({
            'time_based': time_based,
            'price_based': price_based,
            'perceived_time_based': perceived_time_based,
            'perceived_score_based': perceived_score_based
            }, f)