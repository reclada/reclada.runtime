from setuptools import setup

exec(open("_version.py").read())

setup(name='Reclada Coordinator',
      version=__version__,
      description='Coordinatort for Reclada project',
      author='',
      author_email='',
      url='',
      packages=['coordinator', 'coordinator.stage', 'coordinator.db_client', 'coordinator.mb_client', 'coordinator.runner'],
     )