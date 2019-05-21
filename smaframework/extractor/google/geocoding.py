import json
import urllib.request
from urllib.parse import quote
import multiprocessing as mp

def geocode(address, gkey):
    '''
     * Find the latitude and longitude for a given address using Google API.
     *
     * @param  address      The address to lookup.
     * @param  gkey         Google Maps API key.
     * @return tuple        (lat, lng)
    '''
    url = 'https://maps.googleapis.com/maps/api/geocode/json?address='+ quote(address) +'&key=' + gkey
    response = urllib.request.urlopen(url).read().decode("utf-8")
    location = json.loads(response)['results']
    if len(location) > 0:
        location = location[0]['geometry']['location']
        return (location['lat'], location['lng'])
    return None

def geocodeList(addresses, gkey, pool_size=1):
    '''
     * Find the latitude and longitude apirs for a list of addresses using Google API (uses paralel requests for pool_size > 1).
     *
     * @param  addresses    The addresses to lookup.
     * @param  gkey         Google Maps API key.
     * @param  pool_size    Number of paralel workers.
     * @return list         [(lat1, lng1), (lat2, lng2), ...]
    '''
    if pool_size == 1:
        return [geocode(address) for address in addresses]

    pool = mp.Pool(pool_size)
    geocodes = pool.map(geocode, [address for address in addresses])
    pool.close()
    pool.join()

    return geocodes
    