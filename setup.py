import os
from concert import __version__
from setuptools import setup, find_packages


# Install Bash completion script only if installation is run as root
if os.geteuid() != 0:
    data_files = []
else:
    data_files = [('/etc/bash_completion.d', ['extras/completion/concert.sh'])]


setup(
    name='concert',
    version=__version__,
    author='Matthias Vogelgesang',
    author_email='matthias.vogelgesang@kit.edu',
    license='LGPL',
    packages=find_packages(exclude=['*.tests']),
    scripts=['bin/concert'],
    data_files=data_files,
    exclude_package_data={'': ['README.rst']},
    description="Lightweight beamline control system",
    long_description=open('README.rst').read(),
    install_requires=['argparse',
                      'futures',
                      'logbook',
                      'numpy',
                      'prettytable',
                      'pyxdg',
                      'quantities'],
    tests_require=['nose',
                   'testfixtures',
                   'logbook',
                   'quantities',
                   'futures'],
    test_suite='concert.tests',
)
