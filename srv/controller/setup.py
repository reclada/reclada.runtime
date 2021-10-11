from setuptools import setup

exec(open("_version.py").read())

setup(name='Reclada Controller',
      version=__version__,
      description='Controller for Reclada project',
      author='',
      author_email='',
      url='',
      packages=['controller',],
     )
