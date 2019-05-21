import os
import multiprocessing as mp
import pandas as pd
import uuid as IdGenerator
from geopy import distance
from geopy import Point

def organize_file(filename, config):
    location = 'data/linkstream/'

    if not os.path.exists(location):
        os.makedirs(location)

    df = pd.read_csv(filename, header=0)

    if pd.__version__ >= '0.17.0':
        df.sort_values(by=['uid', 'timestamp'], ascending=[1,1], inplace=True)
    else:
        df.sort(['uid', 'timestamp'], ascending=[1,1], inplace=True)

    df = df.reset_index(drop=True).rename(index=str, columns={"uid": "uid_alpha","timestamp": "timestamp_alpha","lat": "lat_alpha","lon": "lon_alpha","layer": "layer_alpha"})
    df2 = df.shift(-1).rename(index=str, columns={"uid_alpha": "uid_beta","timestamp_alpha": "timestamp_beta","lat_alpha": "lat_beta","lon_alpha": "lon_beta","layer_alpha": "layer_beta"})

    df = pd.concat([df, df2], axis=1)
    df = df[df['uid_alpha'] == df['uid_beta']]

    df['distance'] = df.apply(lambda r: distance.distance(Point("%f %f" % (r['lat_alpha'], r['lon_alpha'])), Point("%f %f" % (r['lat_beta'], r['lon_beta']))).meters, axis=1)
    df['time_elapsed'] = df.apply(lambda r: abs(r['timestamp_alpha'] - r['timestamp_beta']), axis=1)

    if 'min_distance' in config.keys():
        min_distance = config['min_distance']
    else:
        min_distance = 500

    if 'max_speed' in config.keys():
        max_speed = 1 / config['max_speed']
    else:
        max_speed = 0.036 # (1 / 100 Km/h) ~= (1 / 27.8 m/s)

    df = df[df['distance'] > min_distance]
    df = df[df['time_elapsed'] > max_speed * df['distance']]

    if 'filename' in config.keys():
        df.to_csv(location + config['filename'], index=False)
    else:
        df.to_csv(location + IdGenerator.uuid4().hex + '.csv', index=False)
    
    return df

def organize(path, **kwargs):
    multiprocess = 'pool_size' in kwargs.keys() and int(kwargs['pool_size']) > 1
    if multiprocess:
        pool_size = int(kwargs['pool_size'])
        pool = mp.Pool(pool_size)

    result = []
    filelist = os.listdir(path)
    for file in filelist:
        if 'file_regex' not in kwargs.keys() or kwargs['file_regex'].match(file):
            if multiprocess:
                result = pool.apply_async(organize_file, args=(os.path.join(path, file), kwargs))
            else:
                result.append(organize_file(os.path.join(path, file), kwargs))

    if multiprocess:
        pool.close()
        pool.join()

    return pd.concat(list(result))

def plot(sequences, key, **kwargs):
    paths = [frame.to_json() for frame in sequences if len(frame) > 0]
    
    length = len(paths)
    if length == 0:
        return False

    result = '['+', '.join(paths)+']'

    with open('templates/google-polyline.html', 'r') as file:
        template = file.read()
    template = template.replace('<?=LIST?>', result).replace('<?=KEY?>', key)

    if 'filename' in kwargs.keys():
        filename = kwargs['filename'] % length
    else:
        filename = 'persistnet-matches-%d.html' % length

    with open('data/results/' + filename, 'w+') as outfile:
        outfile.write(template)