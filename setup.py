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
    url='https://github.com/hanslovsky/imglyb-examples',
    packages=['imglyb_examples'],
    entry_points={
        'console_scripts': [
            'imglyb-examples.butterfly=imglyb_examples.butterfly:main',
            'imglyb-examples.bdv-hello-world=imglyb_examples.bdv_hello_world:main',
            'imglyb-examples.bdv-painter=imglyb_examples.bdv_painter:main',
            'imglyb-examples.qt-awt=imglyb_examples.qt_awt:main',
            'imglyb-examples.views-stack=imglyb_examples.views_stack:main'
        ]
    },
    install_requires=['imglyb', 'jnius', 'scikit-image', 'numpy']
)
