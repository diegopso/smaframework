import smaframework.tool.distribution as Distribution
from sklearn.neighbors import NearestNeighbors
from sklearn.cluster import DBSCAN
from hdbscan import HDBSCAN
import pandas as pd
import numpy as np
import sklearn, json
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from scipy.signal import argrelextrema
from scipy.optimize import curve_fit
import os

def cluster_hdbscan(filename, origin_columns, destination_columns, **kwargs):
    frame = pd.read_csv(filename, header=0, low_memory=True)
    output_file = kwargs['output_file'] if 'output_file' in kwargs.keys() else 'data/results/flow-cluster-' + IdGenerator.uuid4().hex
    pool_size = int(kwargs['pool_size']) if 'pool_size' in kwargs.keys() else 1
    gmaps_key = kwargs['gmaps_key'] if 'gmaps_key' in kwargs.keys() else False
    min_size = kwargs['min_size'] if 'min_size' in kwargs.keys() else int(len(frame)/1000)

    frame = clusterize_hdbscan(frame, origin_columns, destination_columns, min_size, pool_size)

    frame.to_csv(output_file + '.csv')
    return summarize_data(frame, gmaps_key, output_file, origin_columns, destination_columns)

def cluster(filename, origin_columns, destination_columns, **kwargs):
    frame = pd.read_csv(filename, header=0, low_memory=True)

    min_samples = 15 if 'min_samples' not in kwargs.keys() else kwargs['min_samples']
    nnalgorithm = 'ball_tree' if 'nnalgorithm' not in kwargs.keys() else kwargs['nnalgorithm'] # algorithm for NN query {‘auto’, ‘ball_tree’, ‘kd_tree’, ‘brute’}
    output_file = kwargs['output_file'] if 'output_file' in kwargs.keys() else 'data/results/flow-cluster-' + IdGenerator.uuid4().hex
    pool_size = int(kwargs['pool_size']) if 'pool_size' in kwargs.keys() else 1
    gmaps_key = kwargs['gmaps_key'] if 'gmaps_key' in kwargs.keys() else False

    if 'eps' in kwargs.keys():
        eps_origin = kwargs['eps']
        eps_destination = kwargs['eps']
    else:
        sharpener = len(frame) / 1000
        eps_origin = select_eps(frame[origin_columns], min_samples) / sharpener
        eps_destination = select_eps(frame[destination_columns], min_samples) / sharpener
    
    print('INFO: eps(origin=%f, destination=%f) for file=%s' % (eps_origin, eps_destination, output_file))

    frame = clusterize(frame, eps_origin, eps_destination, min_samples, origin_columns, destination_columns, nnalgorithm, pool_size)

    frame.to_csv(output_file + '.csv')
    return summarize_data(frame, gmaps_key, output_file, origin_columns, destination_columns, {
            'min_samples': float(min_samples),
            'eps_origin': float(eps_origin),
            'eps_destination': float(eps_destination)
            })

'''
 * Plot the main flows of a dataset with predefined departure and arrival regions represented by labels.
 *
 * @param frama The data, with the mandatory columns: 'labels_origin', 'labels_destination', and 'flow' ('flow' may be an empty column).
 * @param regions List containing regions and centroids for every label in the labeled data.
 * @param gmaps_key Key used to access Google Maps API.
 * @param output_file Output file location. 
 * @return None
'''
def plot_flows(frame, regions, gmaps_key, output_file, metadata={}):
    frame = frame.groupby(['labels_origin', 'labels_destination']).count().sort_values(by='flow').reset_index()

    flow_threshold = select_knee(frame['flow'].values, output_file)
    frame = frame[frame['flow'] > flow_threshold]

    flows = []
    for (index, row) in frame.iterrows():
        if row['labels_origin'] not in regions.keys() or row['labels_destination'] not in regions.keys():
            continue

        origin_region = [{'lat': point[0], 'lng': point[1]} for point in regions[row['labels_origin']]['region']]    
        destination_region = [{'lat': point[0], 'lng': point[1]} for point in regions[row['labels_destination']]['region']]

        flow = {
            'weight': int(row['flow']),
            'origin_region_id': int(row['labels_origin']),
            'destination_region_id': int(row['labels_destination']),
            'origin_centroid': regions[row['labels_origin']]['centroid'],
            'destination_centroid': regions[row['labels_destination']]['centroid'],
            'origin_region': origin_region,
            'destination_region': destination_region,
            'link': [regions[row['labels_origin']]['centroid'], regions[row['labels_destination']]['centroid']]
        }

        flows.append(flow)

    with open('templates/google-flow.html', 'r') as file:
        template = file.read()
    
    template = template.replace('<?=FLOWS?>', json.dumps(flows)).replace('<?=KEY?>', gmaps_key)
    
    with open(output_file + '.html', 'w+') as outfile:
        outfile.write(template)

    with open(output_file + '.json', 'w+') as outfile:
        json.dump(flows, outfile)

    metadata['flow_threshold'] = float(flow_threshold)
    with open(output_file + '.metadata.json', 'w+') as outfile:
        json.dump(metadata, outfile)

    return frame

def summarize_data(frame, gmaps_key, output_file, origin_columns, destination_columns, metadata={}):
    origin_frame = frame.groupby('labels_origin')
    destination_frame = frame.groupby('labels_destination')
    flow_frame = frame.groupby(['labels_origin', 'labels_destination'])
    
    result = []
    flows = []
    for (group, df) in flow_frame:
        if group[0] == -1 or group[1] == -1:
            continue

        origin = origin_frame.get_group(group[0])
        origin_region = get_region(origin, origin_columns)
        origin_centroid = origin.mean()

        destination = destination_frame.get_group(group[1])
        destination_region = get_region(destination, destination_columns)
        destination_centroid = destination.mean()

        item = {}
        for key in origin_columns:
            item[key] = origin_centroid[key]

        for key in destination_columns:
            item[key] = destination_centroid[key]

        item['flow'] = len(df)

        result.append(item)

        if gmaps_key:
            flow = {
                'weight': len(df),
                'origin_region_id': int(group[0]),
                'destination_region_id': int(group[1]),
                'origin_centroid': {
                    'lat': origin_centroid[origin_columns[0]],
                    'lng': origin_centroid[origin_columns[1]]
                },
                'destination_centroid': {
                    'lat': destination_centroid[destination_columns[0]],
                    'lng': destination_centroid[destination_columns[1]]
                },
                'origin_region': json.loads(origin_region),
                'destination_region': json.loads(destination_region),
                'link': [{
                    'lat': origin_centroid[origin_columns[0]],
                    'lng': origin_centroid[origin_columns[1]]
                }, {
                    'lat': destination_centroid[destination_columns[0]],
                    'lng': destination_centroid[destination_columns[1]]
                }]
            }

            flows.append(flow)

    frame = pd.DataFrame(result)

    flow_threshold = select_knee(frame['flow'].values)

    print('INFO: flow_threshold=%f for file=%s' % (flow_threshold, output_file))

    frame = frame[frame['flow'] > flow_threshold]

    if gmaps_key:
        flows = list(filter(lambda flow: flow['weight'] >= flow_threshold, flows))

        with open('templates/google-flow.html', 'r') as file:
            template = file.read()
        
        template = template.replace('<?=FLOWS?>', json.dumps(flows)).replace('<?=KEY?>', gmaps_key)
        
        with open(output_file + '.html', 'w+') as outfile:
            outfile.write(template)

        with open(output_file + '.json', 'w+') as outfile:
            json.dump(flows, outfile)

    metadata['flow_threshold'] = float(flow_threshold)
    with open(output_file + '.metadata.json', 'w+') as outfile:
        json.dump(metadata, outfile)

    return frame

def get_region(df, columns):
    df = df[columns]
    df.columns = ['lat', 'lon']
    df = Distribution.get_region(df)
    df = '{"lat": '+ df['lat'].map(str) +', "lng": '+ df['lon'].map(str) +', "teta": '+ df['teta'].map(str) +'}'
    return '[' + df.str.cat(sep=',') + ']'

def _interpolate_polynomial(y):
    '''
     * Smoth the data to a polynomial curve.
    '''
    N = len(y)
    x = np.linspace(0, 1, N)

    polynomial_features= PolynomialFeatures(degree=13)
    x = polynomial_features.fit_transform(x.reshape(-1, 1))

    model = LinearRegression()
    model.fit(x, y)
    return model.predict(x)

def _interpolate_exponential(y):
    '''
     * Smooth data to inverse curve: y = alpha / x^beta
    '''
    N = len(y)
    x0 = 0
    x1 = int(.05 * N)
    y0 = y[x0]
    y1 = y[x1]
    alpha = np.log(y1/y0) / x1

    x = np.linspace(0, N, N)
    return y0 * np.exp(x * alpha)

def _interpolate_generic(y):
    '''
     * Use Scipy to estimate the curve.
    '''
    maximum = np.max(y)
    y = y / maximum

    N = len(y)

    # make an estimate for the initial params
    x0 = 0
    x1 = int(.05 * N)
    y0 = y[x0]
    y1 = y[x1]
    alpha = np.log(y1/y0) / x1

    x = np.linspace(0, N, N)
    (coeff, c2) = curve_fit(lambda t, a, b: a*np.exp(b*t), x, y, p0=(y0, alpha), check_finite=False)

    return maximum * coeff[0] * np.exp(x * coeff[1])

def _interpolate(y, interpolator='polynomial'):
    if interpolator == 'polynomial':
        return _interpolate_polynomial(y)
    elif interpolator == 'exponential':
        return _interpolate_exponential(y)
    elif interpolator == 'generic':
        return _interpolate_generic(y)
    
    return y

def select_knee(y, plot2=False, interpolator='polynomial'):
    try:
        # sort data
        y.sort()
        y = y[::-1]

        # cap
        if len(y) > 2500:
            y = y[0:2500]

        # smoothen curvature
        ys = _interpolate(y, interpolator)

        # evaluate curvature equation
        dy = np.gradient(ys)
        ddy = np.gradient(dy)
        k = np.absolute(ddy) / np.power(1+dy*dy, 3/2)

        # evaluate local maxima
        local_maxima = argrelextrema(k, np.greater)

        if plot2:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            plt.clf()

            plt.plot(y)
            plt.plot(ys)
            
            plt.plot(k * np.amax(y) / np.amax(k)) # scaled
            plt.axvline(x=local_maxima[0][0], color='r', linestyle='--')

            plt.legend(['Original', 'Smoothed', 'Curvature', 'Selected'])
            plt.xlabel('Sorted Flow Index')
            plt.ylabel('Flow Magnitude')

            plt.savefig('%s-%d-%d.png' % (plot2, local_maxima[0][0], y[local_maxima[0][0]]))

        # use first local maximum as knee
        return y[local_maxima[0][0]]
    except Exception as e:
        print(e)
        return y[int(len(y) / 10)]

def clusterize_hdbscan(frame, origin_columns, destination_columns, min_size, pool_size=1):
    print('INFO: running HDBSCAN')
    clusterer_origin = HDBSCAN(min_cluster_size=min_size).fit(frame[origin_columns].as_matrix())
    clusterer_destination = HDBSCAN(min_cluster_size=min_size).fit(frame[destination_columns].as_matrix())
    print('INFO: finished HDBSCAN with nclusters(origin=%d, destination=%d)' % (int(clusterer_origin.labels_.max()), int(clusterer_destination.labels_.max())))
    return pd.concat([frame, pd.DataFrame({'labels_origin': clusterer_origin.labels_, 'labels_destination': clusterer_destination.labels_})], axis=1)

def clusterize(frame, eps_origin, eps_destination, min_samples, origin_columns, destination_columns, nnalgorithm='ball_tree', pool_size=1):
    clusterer_origin = None
    clusterer_destination = None
    
    print('INFO: running DBSCAN')
    if sklearn.__version__ > '0.15.2':
        print("\033[93mWARNING: in case of high memory usage error, downgrade scikit: `pip install scikit-learn==0.15.2`\033[0m")
        clusterer_origin = DBSCAN(eps=eps_origin, min_samples=min_samples, n_jobs=pool_size, algorithm=nnalgorithm).fit(frame[origin_columns].as_matrix())
        clusterer_destination = DBSCAN(eps=eps_destination, min_samples=min_samples, n_jobs=pool_size, algorithm=nnalgorithm).fit(frame[destination_columns].as_matrix())
    else:
        clusterer_origin = DBSCAN(eps=eps_origin, min_samples=min_samples).fit(frame[origin_columns].as_matrix())
        clusterer_destination = DBSCAN(eps=eps_destination, min_samples=min_samples).fit(frame[destination_columns].as_matrix())
    print('INFO: finished DBSCAN with nclusters(origin=%d, destination=%d)' % (int(clusterer_origin.labels_.max()), int(clusterer_destination.labels_.max())))

    return pd.concat([frame, pd.DataFrame({'labels_origin': clusterer_origin.labels_, 'labels_destination': clusterer_destination.labels_})], axis=1)

def select_eps(frame, min_samples):
    nbrs = NearestNeighbors(n_neighbors=min_samples).fit(frame)
    distances, indices = nbrs.kneighbors(frame)
    distances = distances[:,distances.shape[1] - 1]
    distances.sort()
    return select_knee(distances)
