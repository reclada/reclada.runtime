from setuptools import setup
from _version import __version__

setup(name='Reclada Coordinator',
      version=__version__,
      description='Coordinatort for Reclada project',
      author='',
      author_email='',
      url='',
      packages=['coordinator', 'coordinator.stage', 'coordinator.db_client', 'coordinator.mb_client', 'coordinator.runner'],
     )
