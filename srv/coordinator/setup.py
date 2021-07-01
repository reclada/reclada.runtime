from setuptools import setup

exec(open("_version.py").read())

setup(name='Distutils',
      version=__version__,
      description='Python Distribution Utilities',
      author='Greg Ward',
      author_email='gward@python.net',
      url='https://www.python.org/sigs/distutils-sig/',
      packages=['distutils', 'distutils.command'],
     )

setup(version=__version__)