try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'name': 'smaframework',
    'version': '0.2',
    'description': 'Urban data integration framework for mobility analisys in smart cities',
    'author': 'Diego Oliveira',
    'url': '--',
    'download_url': '--',
    'author_email': 'diego@lrc.ic.unicamp.br',
    'install_requires': ['pandas', 'numpy', 'scipy', 'scikit-learn', 'geopy', 'matplotlib', 'tweepy', 'pyproj', 'shapely', 'pyclustering', 'image', 'dask', 'fiona', 'haversine', 'hdbscan']
}

setup(**config)
