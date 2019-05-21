import time, datetime
import smaframework.extractor.tomtom.router as TomTomRouter
import multiprocessing as mp

class TrafficSegmentIdentifier(object):
    '''
     * Create routes connecting links in a layer
    '''

    def __init__(self, mlgls):
        self.mlgls = mlgls

    @staticmethod
    def _mergeSections(sections):
        intervals = []
        merged = []
        sections.sort(key=lambda s: s['startInstructionIndex'] if 'startInstructionIndex' in s.keys() else float("inf"))
        
        intervals = []

        sectionIndex = 0
        while 'startInstructionIndex' not in sections[sectionIndex].keys() and sectionIndex < len(sections):
            sectionIndex += 1

        if sectionIndex == len(sections) - 1 and 'startInstructionIndex' not in sections[sectionIndex].keys():
            return []

        currentInterval = (sections[0]['startInstructionIndex'], sections[0]['endInstructionIndex'], sections[0])

        for section in sections[1:]:
            if section['startInstructionIndex'] < currentInterval[0] or section['startInstructionIndex'] > currentInterval[1]:
                intervals.append(currentInterval[2])
                currentInterval = (section['startInstructionIndex'], section['endInstructionIndex'], section)
            elif section['endInstructionIndex'] > currentInterval[1]:
                effectiveSpeed = (currentInterval[2]['effectiveSpeed'] * currentInterval[2]['delayInSeconds'] + section['effectiveSpeed'] * section['delayInSeconds']) / (currentInterval[2]['delayInSeconds'] + section['delayInSeconds'])
                diff = section['endInstructionIndex'] - currentInterval[1]
                prev = currentInterval[1] - currentInterval[0]
                delayInSeconds = (diff / (prev + diff)) * section['delayInSeconds'] + (prev / (prev + diff)) * currentInterval[2]['delayInSeconds']
                currentInterval[2].update({
                    'effectiveSpeed': effectiveSpeed,
                    'delayInSeconds': delayInSeconds,
                    'startInstructionIndex': currentInterval[2]['startInstructionIndex'],
                    'endInstructionIndex': section['endInstructionIndex']
                })
            else:
                pass
    
        intervals.append(currentInterval[2]) # append last interval

        return intervals

    @staticmethod
    def _section2link(section, departureTime, endTime, uid=None, variant=None, sample=None):
        startTime = departureTime + section['startInstruction']['travelTimeInSeconds']
        return {
            'uid': uid,
            'reference': (section['startPoint']['@latitude'], section['startPoint']['@longitude']),
            'destination': (section['endPoint']['@latitude'], section['endPoint']['@longitude']),
            'start': startTime,
            'duration': endTime - startTime,
            'variant': variant,
            'type': section['sectionType'],
            'effectiveSpeed': section['effectiveSpeed'],
            'delay': section['delayInSeconds'],
            'routeOffset': section['startInstruction']['routeOffsetInMeters'],
            'flow': sample
        }

    @staticmethod
    def _completeSections(route, sections, arrivalTime, departureTime, lastInstructionIndex, lastPointIndex, uid, variant, sample):
        '''
         * Adds missing sections to connect route and transform sections in links.
         *
         * @param route                 The route to be completed.
         * @param section               The original list of sections retrieved from TomTom API. 
         * @param arrivalTime           The arrival time of the whole trip.
         * @param departureTime         The departure time of the trip.
         * @param lastInstructionIndex  The the index of the last instruction of the trip in the TomTom response.
         * @param lastPointIndex        The the index of the last point of the trip in the TomTom response.
        '''
        links = []
        for (i, section) in enumerate(sections):
            section['startInstruction'] = route['guidance']['instructions']['instruction'][section['startInstructionIndex']]
            section['endInstruction'] = route['guidance']['instructions']['instruction'][section['endInstructionIndex']]

            appendSection = None
            if i > 0 and section['startInstructionIndex'] != sections[i-1]['endInstructionIndex']: # add missing section from previous to this
                appendSection = {
                    "startPointIndex": sections[i-1]['endPointIndex'],
                    "endPointIndex": section['startPointIndex'],
                    "startPoint": sections[i-1]['endPoint'],
                    "endPoint": section['startPoint'],
                    "startInstructionIndex": sections[i-1]['endInstructionIndex'] + 1,
                    "endInstructionIndex": section['startInstructionIndex'] - 1,
                    "sectionType": "DEFAULT",
                    "simpleCategory": "",
                    "effectiveSpeed": None,
                    "delayInSeconds": 0,
                    "magnitudeOfDelay": 0,
                    "startInstruction": route['guidance']['instructions']['instruction'][sections[i-1]['endInstructionIndex'] + 1],
                    "endInstruction": route['guidance']['instructions']['instruction'][section['startInstructionIndex'] - 1],
                }
            elif i == 0 and section['startInstructionIndex'] != 0: # add missing section from 0 to this
                appendSection = {
                    "startPointIndex": 0,
                    "endPointIndex": section['startPointIndex'],
                    "startPoint": route['leg']['points']['point'][0],
                    "endPoint": section['startPoint'],
                    "startInstructionIndex": 0,
                    "endInstructionIndex": section['startInstructionIndex'] - 1,
                    "sectionType": "DEFAULT",
                    "simpleCategory": "",
                    "effectiveSpeed": None,
                    "delayInSeconds": 0,
                    "magnitudeOfDelay": 0,
                    "startInstruction": route['guidance']['instructions']['instruction'][0],
                    "endInstruction": route['guidance']['instructions']['instruction'][section['startInstructionIndex'] - 1],
                }

            if appendSection:
                links.append(TrafficSegmentIdentifier._section2link(appendSection, departureTime, departureTime + section['startInstruction']['travelTimeInSeconds'], uid, variant, sample))

            timestamp = 0
            if section['endInstructionIndex'] == lastInstructionIndex:
                timestamp = arrivalTime
            else:
                timestamp = departureTime + route['guidance']['instructions']['instruction'][section['endInstructionIndex'] + 1]['travelTimeInSeconds']

            links.append(TrafficSegmentIdentifier._section2link(section, departureTime, timestamp, uid, variant, sample))

            # add missing final section
            if i == len(sections) - 1 and section['endInstructionIndex'] != lastInstructionIndex:
                appendSection = {
                    "startPointIndex": section['endPointIndex'],
                    "endPointIndex": lastPointIndex,
                    "endPoint": route['leg']['points']['point'][-1],
                    "startPoint": section['endPoint'],
                    "startInstructionIndex": section['endInstructionIndex'] + 1,
                    "endInstructionIndex": lastInstructionIndex,
                    "sectionType": "DEFAULT",
                    "simpleCategory": "",
                    "effectiveSpeed": None,
                    "delayInSeconds": 0,
                    "magnitudeOfDelay": 0,
                    "startInstruction": route['guidance']['instructions']['instruction'][section['endInstructionIndex'] + 1],
                    "endInstruction": route['guidance']['instructions']['instruction'][lastInstructionIndex],
                }
                links.append(TrafficSegmentIdentifier._section2link(appendSection, departureTime, arrivalTime, uid, variant, sample))

        return links

    @staticmethod
    def _getRoute(data):
        (index, sample, config, tomtomKey) = data
        sample['reference'] = tuple(sample['reference'])
        sample['destination'] = tuple(sample['destination'])
        uid = sample['uid'] if 'uid' in sample.keys() else None

        if sample['reference'] == sample['destination']:
            return []

        routes = TomTomRouter.getRoute(sample['reference'], sample['destination'], tomtomKey, config['max_alternatives'])
        
        direct = False
        results = []
        for (variant, route) in enumerate(routes):
            lastInstructionIndex = len(route['guidance']['instructions']['instruction']) - 1
            lastPointIndex = len(route['leg']['points']['point']) - 1

            departureTime = ''.join(route['summary']['departureTime'].rsplit(':', 1))
            departureTime = time.mktime(datetime.datetime.strptime(departureTime, "%Y-%m-%dT%H:%M:%S%z").timetuple())

            arrivalTime = ''.join(route['summary']['arrivalTime'].rsplit(':', 1))
            arrivalTime = time.mktime(datetime.datetime.strptime(arrivalTime, "%Y-%m-%dT%H:%M:%S%z").timetuple())

            if len(route['sections']['section']) == 0:
                if direct:
                    continue
                
                direct = True
                results.append({
                  "uid": uid,
                  "variant": variant,
                  "reference": sample['reference'],
                  "destination": sample['destination'],
                  "start": departureTime,
                  "duration": arrivalTime - departureTime,
                  "routeOffset": 0,
                  "type": "DEFAULT",
                  "effectiveSpeed": None,
                  "delay": 0, 
                  "flow": sample
                });

                continue

            sections = TrafficSegmentIdentifier._mergeSections(route['sections']['section'])
            links = TrafficSegmentIdentifier._completeSections(route, sections, arrivalTime, departureTime, lastInstructionIndex, lastPointIndex, uid, variant, sample)
            results.extend(links)

        return results

    def route(self, layer, tomtomKey, **kwargs):
        '''
         * Create routes connecting links in a layer.
         *
         * @param layer         The linkstream layer to be transformed.
         * @param tomtomKey     The key to access TomTom API.
        '''
        config = {
            'pool_size': 1,
            'max_alternatives': 2,
            'out_layer': layer + '_traffic'
        }
        config.update(kwargs)

        data = self.mlgls.layers[layer]
        if data['type'] != 'linkstream':
            raise Exception('The transformed layer must be an linkstream (containing reference and destination).')

        linkstream = self.mlgls.getData(layer)

        routes = []
        if config['pool_size'] == 1:
            for (index, sample) in enumerate(linkstream):
                route = TrafficSegmentIdentifier._getRoute((index, sample, config, tomtomKey))
                routes.append(route)
        else:
            pool = mp.Pool(config['pool_size'])
            routes = pool.map(TrafficSegmentIdentifier._getRoute, [(index, sample, config, tomtomKey) for (index, sample) in enumerate(linkstream)])
            pool.close()
            pool.join()

        routes = [item for sublist in routes for item in sublist]
        routes.sort(key=lambda r: r['start'])

        self.mlgls.addLinkstreamLayer(routes, config['out_layer'])

        return self.mlgls.getData(config['out_layer'])
