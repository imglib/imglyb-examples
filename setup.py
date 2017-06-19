import os
import glob
from subprocess import call
from distutils.core import setup
from distutils.command.build_py import build_py

setup(
    name='imglyb-examples',
    version='0.0.1',
    author='Philipp Hanslovsky',
    author_email='hanslovskyp@janelia.hhmi.org',
    description='Examples for the imglyb.',
    packages=['imglyb-examples'],
    install_requires=['imglyb', 'jnius', 'scikit-image', 'numpy']
)
