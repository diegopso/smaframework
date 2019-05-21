class Segmenter(object):
    '''
     * Segments routes based on criterias.
    '''

    def __init__(self, mlgls):
        self.mlgls = mlgls

    @staticmethod
    def key(link, criteria):
        '''
         * Creates a key for a given link if it satisfies all criteria.
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

    def segment(self, layer, criteria, **kwargs):
        '''
         * Split a layer into many according to specific criterias.
         * 
         * @param   layer       The name of the layer.
         * @param   criteria    The criteria dictionary where elements `True` are taken as key components and others are used as filters.
         * @return  layers      A list containing all names of layers generated.
        '''
        config = {
            'index': False,
        }
        config.update(kwargs)

        results = {}
        linkstream = self.mlgls.getData(layer)
        for link in linkstream:
            key = Segmenter.key(link, criteria)
            if key is None:
                continue

            if key not in results.keys():
                results[key] = []
            results[key].append(link)

        layers = []
        for key in results.keys():
            l = '%s_%s' % (layer, key)
            layers.append(l)
            self.mlgls.addLinkstreamLayer(results[key], '%s_%s' % (layer, key), index=config['index'])

        return layers