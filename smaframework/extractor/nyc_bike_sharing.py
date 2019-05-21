import json
import urllib.request

def get(status="In Service"):
    '''
     * Load stations of bike sharing.
     *
     * @param  status - A status to filter stations (e.g., "In Service", "Not In Service", None; default: "In Service").
     * @return stations - A list with stations and their data.
    '''
    url = 'https://feeds.citibikenyc.com/stations/stations.json'
    response = urllib.request.urlopen(url).read().decode("utf-8")
    stations = json.loads(response)

    if not status:
    	return stations['stationBeanList']

    result = []
    for s in stations['stationBeanList']:
    	if s['statusValue'] == status:
    		result.append(s)

    return result


    			