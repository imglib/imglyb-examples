import os
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.md')) as f:
    imglyb_examples_long_description = f.read()

version_info = {}
with open(os.path.join(here, 'imglyb_examples', 'version_info.py')) as fp:
    exec(fp.read(), version_info)
version = version_info['_version']

install_requires=[
    'imglyb>=0.3.4',
    'pyjnius',
    'scikit-image',
    'numpy'],

setup(
    name='imglyb-examples',
    version=version.version(),
    author='Philipp Hanslovsky',
    author_email='hanslovskyp@janelia.hhmi.org',
    description='Examples for imglyb.',
    long_description=imglyb_examples_long_description,
    long_description_content_type='text/markdown',
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
    isntall_requires=install_requires,
    python_requires='>=3'
)
