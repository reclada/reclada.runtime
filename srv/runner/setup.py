from setuptools import setup

exec(open("_version.py").read())

setup(name='Reclada Runner',
      version=__version__,
      description='Runner for Reclada project',
      author='',
      author_email='',
      url='',
      packages=['runner'],
     )