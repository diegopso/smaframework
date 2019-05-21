import time
import scipy.spatial
from haversine import haversine
import smaframework.tool.conversor as Conversor
import smaframework.common.search as Searcher

class mlgls(object):
	'''
	 * Multi-layer Geo Linkstream.
	 * Represents linkstream data as a multilayer structured indexed on space (uses KDTree).
	'''

	'''
	 * Store the layers.
	'''
	layers = {}
			
	@staticmethod
	def createLinkstreamLayer(ls, layer, **kwargs):
		'''
		 * Create a linkstream layer.
		 * 
		 * @param ls 	Linkstream data as a list. Each sample must contain: reference: (lat, lon), destination: (lat, lon), start, and duration properties.
		 * @param layer Name of the added layer.
		'''
		config = {
			'leafsize': 25,
			'index': True
		}
		config.update(kwargs)

		origins = []
		for sample in ls:
			origins.append(sample['reference'])

		index = None
		if config['index']:
			index = scipy.spatial.cKDTree(origins, leafsize=config['leafsize'])


		return {
			'type': 'linkstream',
			'data': ls,
			'index': index,
		}

	def addLinkstreamLayer(self, ls, layer, **kwargs):
		'''
		 * Add a linkstream layer.
		 * 
		 * @param ls 	Linkstream data as a list. Each sample must contain: reference: (lat, lon), destination: (lat, lon), start, and duration properties.
		 * @param layer Name of the added layer.
		'''
		self.layers[layer] = mlgls.createLinkstreamLayer(ls, layer, **kwargs)

	@staticmethod
	def createStaticLayer(g, layer, **kwargs):
		'''
		 * Add a linkstream layer.
		 * 
		 * @param g 	Graph data as a list. Each sample must contain: reference: (lat, lon).
		 * @param layer Name of the added layer.
		'''
		config = {
			'leafsize': 25,
			'index': True
		}
		config.update(kwargs)

		data = [sample['reference'] for sample in g]

		index = None
		if config['index']:
			index = scipy.spatial.cKDTree(data, leafsize=config['leafsize'])

		return {
			'type': 'static',
			'data': g,
			'index': index
		}

	def addStaticLayer(self, g, layer, **kwargs):
		'''
		 * Add a linkstream layer.
		 * 
		 * @param ls 	Linkstream data as a list. Each sample must contain: reference: (lat, lon).
		 * @param layer Name of the added layer.
		'''
		self.layers[layer] = mlgls.createStaticLayer(g, layer, **kwargs)

	def addDynamicLayer(self, func, layer, layerType='linkstream', **kwargs):
		'''
		 * Add a layer dependent on time.
		 * 
		 * @param func 		A function to call and receive the data, this function receives unixtimestamp as param.
		 * @param layer 	Name of the added layer.
		 * @param layerType Type of the dynamic layer, default: 'linkstream'.
		'''
		config = {
			'leafsize': 25,
			'cache': 60 * 60,
		}
		config.update(kwargs)

		self.layers[layer] = {
			'type': 'dynamic',
			'use_as': layerType,
			'config': config,
			'data': func,
			'cached': None,
			'cached_index': None
		}

	def removeLayer(self, layer):
		'''
		 * Remove a layer from memory.
		 * 
		 * @param layer The layer to be removed.
		'''
		import gc
		self.layers[layer] = None
		gc.collect()

	def subLayer(self, layer, start, end, **kwargs):
		'''
		 * Creates a layer containing entries from another in a specified time interval.
		 * 
		 * @param 	layer 	Name of the layer.
		 * @param 	start 	The start of the resulting layer.
		 * @param 	end 	The end of the resulting layer.
		 * @return	string 	The name of the resulting layer.
		'''
		if not (self.layers[layer]['type'] == 'linkstream' or 'use_as' in self.layers[layer].keys() and self.layers[layer]['use_as'] == 'linkstream'):
			return False

		config = {
			'index': False,
			'out_layer': '%s_%d_%d' % (layer, start, end)
		}
		config.update(kwargs)

		linkstream = self.getData(layer)
		searchStart = Searcher.binarySearch(linkstream, start, key=lambda link: link['start'])
		searchLength = len(linkstream)

		results = []
		for i in range(searchStart, searchLength):
			if linkstream[i]['start'] > end:
				break
			results.append(linkstream[i])

		self.addLinkstreamLayer(results, config['out_layer'], **config)
		return config['out_layer']

	def getData(self, layer):
		'''
		 * Get raw data from a layer.
		 * 
		 * @param layer Name of the added layer.
		'''
		if self.layers[layer]['type'] == 'dynamic':
			timestamp = int(time.time())

			if self.layers[layer]['cached'] and timestamp < self.layers[layer]['cached_at'] + self.layers[layer]['config']['cache']:
				return self.layers[layer]['cached']

			self.layers[layer]['cached'] = self.layers[layer]['data'](timestamp)
			self.layers[layer]['cached_at'] = timestamp
			return self.layers[layer]['cached']
		else:
			return self.layers[layer]['data']

	def getIndex(self, layer):
		'''
		 * Get indexed (KDTree) data from a layer.
		 * 
		 * @param layer Name of the added layer.
		'''
		if self.layers[layer]['type'] == 'dynamic':
			timestamp = int(time.time())
			
			if self.layers[layer]['cached_index'] and timestamp < self.layers[layer]['cached_at'] + self.layers[layer]['config']['cache']:
				return self.layers[layer]['cached_index']

			data = self.getData(layer)
			if self.layers[layer]['use_as'] == 'static':
				dlayer = mlgls.createStaticLayer(data, self.layers[layer]['use_as'], **self.layers[layer]['config'])
				self.layers[layer]['cached_index'] = dlayer['index']
			elif self.layers[layer]['use_as'] == 'linkstream':
				dlayer = mlgls.createLinkstreamLayer(data, self.layers[layer]['use_as'], **self.layers[layer]['config'])
				self.layers[layer]['cached_index'] = dlayer['index']
			
			return self.layers[layer]['cached_index']
		else:
			return self.layers[layer]['index']

	def _getNearestNeighborhood(self, layer, query, k, maxDistance=None):
		tree = self.getIndex(layer)
		raw = self.getData(layer)

		if not maxDistance:
			maxDistance = float('inf')
		else:
			maxDistance = Conversor.meters2geodist(maxDistance, True, query[0])

		results = tree.query(query, k=k, distance_upper_bound=maxDistance)
		
		if isinstance(results[0], float):
			results = ([results[0]], [results[1]])

		if results[0][0] == float('inf'): # no results
			return []

		data = []
		for (distance, i) in zip(*results):
			data.append({'distance': haversine(raw[i]['reference'], query) * 1000, 'data': raw[i]})

		return data

	def getNearestNeighborhood(self, query, layers, k, maxDistance=None):
		'''
		 * Get closest points to a specified query.
		 * 
		 * @param query 		The reference point.
		 * @param layers 		The layers to be searched.
		 * @param k 	 		The amount of points to be found.
		 * @param maxDistance 	The max distance in meters to search, for optimization (potentially limits the amount of results).
		'''
		if isinstance(layers, str):
			layers = [layers]

		result = {}
		for layer in layers:
			result[layer] = self._getNearestNeighborhood(layer, query, k, maxDistance)

		return result

	def transformers(self, module):
		import importlib, inspect
		module = importlib.import_module(module)
		(name, class_) =  inspect.getmembers(module, inspect.isclass)[0]
		return class_(self)
