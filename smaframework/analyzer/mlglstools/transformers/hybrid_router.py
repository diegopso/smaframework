import itertools, time, datetime
from haversine import haversine
import smaframework.extractor.tomtom.router as TomTomRouter
import smaframework.extractor.google.directions as GoogleDirectionsExtractor
import smaframework.extractor.uber as UberExtractor
import smaframework.extractor.openweathermap as OpenWeatherMapExtractor
import smaframework.tool.constants as Constants

class HybridRouter(object):
    '''
     * Creates hybrid routes for routes in layer.
    '''

    def __init__(self, mlgls):
        self.mlgls = mlgls
        self.precision = 0.025
    
    @staticmethod
    def _classify(link, classifier):
        '''
         * Checks if a link satisfies the criterias in classifier.
         * 
         * @param link          The link.
         * @param classifier    The classifier dictionary where elements are used as filters.
        '''
        for key in classifier.keys():
            if classifier[key] != link[key]:
                return False
        return True

    @staticmethod
    def _key(link, criteria):
        '''
         * Creates a key for a given link if it satisfies all filters.
         * 
         * @param link      The link.
         * @param criteria  The criteria dictionary where elements `True` are taken as key components and others are used as filters.
        '''
        key = ''
        for c in criteria.keys():
            if criteria[c] is True:
                key += '-%s' % str(link[c])
            elif link[c] != criteria[c]:
                return None
        return key[1:]

    @staticmethod
    def _step2link(step, start):
        '''
         * Converts a step in of route instruction in a link of the MLGLS.
         * 
         * @param step      The step.
         * @param start     The start time of he step.
        '''

        step.update({
            'reference': tuple(step['origin']),
            'destination': tuple(step['destination']),
            'start': int(start) if start else None,
            'travel_mode': step['travel_mode'].lower(),
            'wait': step['wait'],
        })
        
        if 'origin' in step.keys():
            del step['origin']

        if 'address_keywords' in step.keys():
            del step['address_keywords']

        return step

    def _tomtomRoute2link(route, mode, prices):
        '''
         * Converts a TomTom route in a link of the MLGLS.
         * 
         * @param route The route.
         * @param mode  The mode used in the route.
        '''
        strTime = route['summary']['departureTime'][:-3] + route['summary']['departureTime'][-2:] if route['summary']['departureTime'][-3] == ':' else route['summary']['departureTime']
        return {
            'reference': tuple((route['leg']['points']['point'][0]['@latitude'], route['leg']['points']['point'][0]['@longitude'])),
            'destination': tuple((route['leg']['points']['point'][-1]['@latitude'], route['leg']['points']['point'][-1]['@longitude'])),
            'start': int(time.mktime(datetime.datetime.strptime(strTime, "%Y-%m-%dT%H:%M:%S%z").timetuple())),
            'duration': int(route['summary']['travelTimeInSeconds']),
            'travel_mode': mode,
            'price': prices[mode](route) if mode in prices.keys() else 0,
            'wait': int(route['summary']['trafficDelayInSeconds']),
            'distance': int(route['summary']['lengthInMeters']),
        }

    @staticmethod
    def _completeRoutes(start, start_transition, end, end_transition, routes, config):
        if len(routes) == 0:
            return None

        distance = haversine(start, start_transition)
        startTime = routes[0][0]['start']
        travelMode = routes[0][0]['travel_mode']
        access = []
        egress = []

        if distance > 0.1:
            start_taxi_segment = UberExtractor.estimate(config['uber_key'], start, start_transition, 1, config['uber_modality'])
            tomtomRoute = TomTomRouter.getRoute(tuple(start), tuple(start_transition), config['tomtom_key'], 0, travelMode='car')
            if len(tomtomRoute) > 1:
                traffic = tomtomRoute[0]['summary']['trafficDelayInSeconds']
                start_taxi_segment = HybridRouter._step2link({
                        "duration": start_taxi_segment['duration'],
                        "congested_time": int(traffic),
                        "wait": start_taxi_segment['wait'] if 'wait' in start_taxi_segment.keys() else 0,
                        "travel_mode": "TAXI",
                        "vehicle_type": config['uber_modality'],
                        "origin": start_taxi_segment['origin'],
                        "distance": start_taxi_segment['distance'],
                        "destination": start_taxi_segment['destination'],
                        "price":  start_taxi_segment['price']
                    }, startTime)
                access.append(start_taxi_segment)

        if distance > 0.01:
            start_walking_segment = HybridRouter._step2link({
                    "duration": int(distance * 1000 / Constants.avg_walking_speed),
                    "congested_time": 0,
                    "wait": 0,
                    "travel_mode": "walking",
                    "vehicle_type": None,
                    "origin": start,
                    "distance": int(distance * 1000),
                    "destination": start_transition,
                    "price":  0
                }, startTime)
            access.append(start_walking_segment)

        if travelMode == 'bycicle' and distance > 0.1:
            routes = GoogleDirectionsExtractor.extract_single(config['google_maps_key'], start, start_transition, now, 'transit', config['prices'], transitMode='subway|tram|bus', alternatives='false')

            for (i, step) in enumerate(routes[0]):
                HybridRouter._step2link(step, step['departure_time'])
                if i > 0 and step['travel_mode'] == 'TRANSIT':
                    step['wait'] = step['departure_time'] - routes[0][i - 1]['start'] + routes[0][i - 1]['duration']

            access.append(routes[0])

        distance = haversine(end, end_transition)

        if distance > 0.1:
            end_taxi_segment = UberExtractor.estimate(config['uber_key'], end_transition, end, 1, config['uber_modality'])
            tomtomRoute = TomTomRouter.getRoute(tuple(end_transition), tuple(end), config['tomtom_key'], 0, travelMode='car')
            if len(tomtomRoute) > 1:
                traffic = tomtomRoute[0]['summary']['trafficDelayInSeconds']
                end_taxi_segment = HybridRouter._step2link({
                        "duration": end_taxi_segment['duration'],
                        "congested_time": int(traffic),
                        "wait": end_taxi_segment['wait'] if 'wait' in end_taxi_segment.keys() else 0,
                        "travel_mode": "TAXI",
                        "vehicle_type": config['uber_modality'],
                        "origin": end_taxi_segment['origin'],
                        "distance": end_taxi_segment['distance'],
                        "destination": end_taxi_segment['destination'],
                        "price":  end_taxi_segment['price']
                    }, None)
                egress.append(end_taxi_segment)

        if distance > 0.01:
            end_walkig_segment = HybridRouter._step2link({
                    "duration": int(distance * 1000 / Constants.avg_walking_speed),
                    "congested_time": 0,
                    "wait": 0,
                    "travel_mode": "walking",
                    "vehicle_type": None,
                    "origin": end_transition,
                    "distance": int(distance * 1000),
                    "destination": end,
                    "price":  0
                }, None)
            egress.append(end_walkig_segment)

        if travelMode == 'bycicle' and distance > 0.1:
            routes = GoogleDirectionsExtractor.extract_single(config['google_maps_key'], end_transition, end, now, 'transit', config['prices'], transitMode='subway|tram|bus', alternatives='false')

            for (i, step) in enumerate(routes[0]):
                HybridRouter._step2link(step, None)
                if i > 0 and step['travel_mode'] == 'TRANSIT':
                    step['wait'] = step['departure_time'] - routes[0][i - 1]['start'] + routes[0][i - 1]['duration']

            egress.append(routes[0])

        results = []
        for route in routes:
            for option in access:
                clone = route.copy()

                for step in clone:
                    step['start'] += int(option['duration'])

                clone[0]['reference'] = option['destination']
                clone.insert(0, option)
                results.append(clone)

        routes = results
        results = []
        for route in routes:
            for option in egress:
                clone = route.copy()
                option['start'] = int(route[-1]['start'] + route[-1]['duration'] + 1)
                clone[-1]['destination'] = option['reference']
                clone.append(option)
                results.append(clone)
            
        return results

    def _getRoutes(self, transitionPoints, start, end, alternativeLayers, config):
        used_segments = {}
        combinations = itertools.product(*transitionPoints)
        now = int(time.time()) + 60

        tomtomRoute = TomTomRouter.getRoute(tuple(start), tuple(end), config['tomtom_key'], 0, travelMode='car')
        if len(tomtomRoute) == 0:
            return []

        full_taxi_option = UberExtractor.estimate(config['uber_key'], start, end, 1, config['uber_modality'])
        traffic = tomtomRoute[0]['summary']['trafficDelayInSeconds']
        full_taxi_option = HybridRouter._step2link({
                "duration": full_taxi_option['duration'],
                "congested_time": int(traffic),
                "wait": full_taxi_option['wait'] if 'wait' in full_taxi_option.keys() else 0,
                "travel_mode": "TAXI",
                "vehicle_type": config['uber_modality'],
                "origin": full_taxi_option['origin'],
                "distance": full_taxi_option['distance'],
                "destination": full_taxi_option['destination'],
                "price":  full_taxi_option['price']
            }, now)


        distance = 0
        tomtomRoute = TomTomRouter.getRoute(tuple(start), tuple(end), config['tomtom_key'], 0, travelMode='pedestrian')
        if len(tomtomRoute) == 0:
            distance = int(haversine(tuple(start), tuple(end)) * 1000)
        else:
            distance = int(tomtomRoute[0]['summary']['lengthInMeters'])
            
        full_walking_option = HybridRouter._step2link({
                    "duration": int(distance / Constants.avg_walking_speed),
                    "congested_time": 0,
                    "wait": 0,
                    "travel_mode": "walking",
                    "vehicle_type": None,
                    "origin": start,
                    "distance": distance,
                    "destination": end,
                    "price":  0
                }, now)

        results = [[full_taxi_option],[full_walking_option]]

        for pair in combinations:
            if haversine(*pair) < self.precision:
                continue

            # get closest points in layer, one start and one end.
            starts = self.mlgls.getNearestNeighborhood(pair[0], alternativeLayers.keys(), 1, config['maxDetour'])
            ends = self.mlgls.getNearestNeighborhood(pair[1], alternativeLayers.keys(), 1, config['maxDetour'])

            for alternativeLayer in alternativeLayers.keys():
                # skip if there is no in or out points for a given routing approach
                if len(starts[alternativeLayer]) == 0 or len(ends[alternativeLayer]) == 0:
                    continue

                start_transition = starts[alternativeLayer][0]['data']['reference']
                end_transition = ends[alternativeLayer][0]['data']['reference']

                # skip if the start and end are too close
                if haversine(start_transition, end_transition) < self.precision:
                    continue

                if alternativeLayers[alternativeLayer] not in used_segments.keys():
                    used_segments[alternativeLayers[alternativeLayer]] = []

                # skip if the same segment has been calculated using the same routing approach
                if any([haversine(segment[0], start_transition) < self.precision and haversine(segment[1], end_transition) < self.precision for segment in used_segments[alternativeLayers[alternativeLayer]]]):
                    continue

                used_segments[alternativeLayers[alternativeLayer]].append((start_transition, end_transition))

                if alternativeLayers[alternativeLayer].startswith('transit'):
                    transitMode = alternativeLayers[alternativeLayer].split('=')
                    if len(transitMode) > 1:
                        transitMode = transitMode[1]
                    else:
                        transitMode = 'bus|tram|subway'

                    routes = GoogleDirectionsExtractor.extract_single(config['google_maps_key'], start_transition, end_transition, now, 'transit', config['prices'], transitMode=transitMode, alternatives='false')

                    for route in routes:
                        if route[0]['travel_mode'] == 'WALKING' and len(route) > 1:
                            route[1]['origin'] = route[0]['origin']
                            route.pop(0)

                        if route[-1]['travel_mode'] == 'WALKING' and len(route) > 1:
                            route[-2]['destination'] = route[-1]['destination']
                            route.pop()

                        for (i, step) in enumerate(route):
                            HybridRouter._step2link(step, step['departure_time'])
                            if i > 0 and step['travel_mode'] == 'TRANSIT':
                                step['wait'] = step['departure_time'] - route[i - 1]['start'] + route[i - 1]['duration']

                elif alternativeLayers[alternativeLayer] in ['car', 'truck', 'taxi', 'bus', 'van', 'motorcycle', 'bicycle', 'pedestrian']:
                    routes = TomTomRouter.getRoute(start_transition, end_transition, config['tomtom_key'], 0, travelMode=alternativeLayers[alternativeLayer])

                    if routes is None:
                        continue

                    alternatives = []
                    for route in routes:
                        link = HybridRouter._tomtomRoute2link(route, alternativeLayers[alternativeLayer], config['prices'])
                        alternatives.append([link])
                    routes = alternatives
                else:
                    continue

                routes = HybridRouter._completeRoutes(start, start_transition, end, end_transition, routes, config)
                
                if routes:
                    results.extend(routes)

        return results

    def _isWeatherConstrained(self, route, config):
        '''
         * Checks wether a rute is weather constrained or not.
         *
         * @param route  The evaluated route.
         * @param config The config used to check the routes. The position `config['weather_constraints']` is expected to be a dict 
                         containing the route modes as keys and a list with the constraints as value.
         * @return       `True` if the route is constrained, and `False` otherwise.
        '''
        if len(config['weather_constraints'].keys()) == 0:
            return False

        for step in route:
            lat, lon = ((step['reference'][0]+step['destination'][0])/2, (step['reference'][1]+step['destination'][1])/2)
            data = OpenWeatherMapExtractor.get(lat, lon, config['openweathermap_appid'])

            for mode in config['weather_constraints'].keys():
                if step['travel_mode'] != mode:
                    continue

                if any([weather['description'] in config['weather_constraints'][mode] for weather in data['weather']]):
                    return True

        return False

    def _filterWeatherConstrainedRoutes(self, trip, config):
        '''
         * Removes weather constrained routes according to config.
         *
         * @param trip      The trip containing the route candidates.
         * @param config    The config used to check the routes. The position `config['weather_constraints']` is expected to be a dict 
                            containing the route modes as keys and a list with the constraints as value.
         * @return          The list of routes not constrained by weather.
        '''
        results = []
        for route in trip:
            if not self._isWeatherConstrained(route, config):
                results.append(route)
        return results

    def route(self, layer, alternativeLayers, **kwargs):
        '''
         * Calculate hybrid routes for a given layer.
         *
         * @param layer                 The analyzed layer.
         * @param alternativeLayers     Layers to use as alternatives for the original route.
         *                              A dict like `{layerName: travelMode}`, where (travelMode in ['car', 'truck', 'taxi', 'bus', 'van', 'motorcycle', 'bicycle', 'pedestrian', 'transit']).
         *                              `transit` mode also may be specified as: transit=mode1|mode2|mode3 (for mode in ['bus', 'subway', 'train', 'tram', 'rail']).
        '''
        if not (self.mlgls.layers[layer]['type'] == 'linkstream' or 'use_as' in self.mlgls.layers[layer].keys() and self.mlgls.layers[layer]['use_as'] == 'linkstream'):
            return False

        config = {
            'maxAlternatives': 1,
            'maxDetour': float('inf'),
            'classifier': {
                'type': 'TRAFFIC'
            },
            'weather_constraints': {
                'walking': ['shower rain', 'rain', 'thunderstorm'],
                'bicycle': ['shower rain', 'rain', 'thunderstorm', 'snow']
            },
            'keygen': {
                'uid': True,
                'variant': True
            },
        }
        config.update(kwargs)
        
        routes = {}
        linkstream = self.mlgls.getData(layer)

        for link in linkstream:
            if not HybridRouter._classify(link, config['classifier']):
                continue

            key = HybridRouter._key(link, config['keygen'])
            if key not in routes.keys():
                routes[key] = {
                    'start_transition_points': [],
                    'end_transition_points': []
                }

            routes[key]['start_transition_points'].append(link['reference'])
            routes[key]['end_transition_points'].append(link['destination'])

        results = []
        for variant in routes.keys():
            start = linkstream[0]['reference']
            end = linkstream[-1]['destination']

            if all([haversine(start,  stp) > self.precision for stp in routes[variant]['start_transition_points']]):
                routes[variant]['start_transition_points'].insert(0, start)
            
            if all([haversine(end, etp) > self.precision for etp in routes[variant]['end_transition_points']]):
                routes[variant]['end_transition_points'].append(end)

            ls = self._getRoutes([routes[variant]['start_transition_points'], routes[variant]['end_transition_points']], start, end, alternativeLayers, config)

            variant_routes = []
            for trip in ls:
                remmaining = self._filterWeatherConstrainedRoutes(trip, config)
                if len(remmaining) > 0:
                    variant_routes.append(remmaining)

            results.extend(variant_routes)
        return (results, linkstream[0]['flow'] if 'flow' in linkstream[0].keys() else None)