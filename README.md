# imglyb-examples

This is a repository of examples for [imglyb](https://github.com/imglib/imglyb).

## Dependencies
All dependencies will be installed automatically when installing `imglyb-examples` through conda.
 - [imglyb](https://github.com/hanslovsky/imglyb)
 - [numpy](http://www.numpy.org)
 - [scikit-image](https://github.com/scikit-image/scikit-image)
 
[imglyb](https://github.com/hanslovsky/imglyb) is available on conda or you can install it manually following the build instructions. All other depdendencies are available through your package manager, `pip`, or various anaconda channels.

## Install

### Manual
First, make sure that all dependencies are installed, then run
```bash
python setup.py install
```

### Conda
```bash
conda install -c hanslovsky imglyb-examples
```
If `imglyb` was not previously installed, re-source the current conda environment after installing to set the environment properly.

## Run
These examples are available.
```bash
# bash
# Basic visualization and application of Python and ImgLib2 filters
python -m imglyb_examples.butterfly
# Python implemented overlays for BigDataViewer
python -m imglyb_examples.bdv_hello_world
# Python implementation of a painting tool for BigDataViewer
python -m imglyb_examples.bdv_painter
# Embed BigDataViewer in Qt application (only Linux, and Qt and python-xlib dependencies)
python -m imglyb_examples.qt_awt
# Basic visualization of series of 2D NumPy arrays
python -m imglyb_examples.views_stack
```
I recommend starting your own code from these examples and extend as you need. On Linux and Windows you can run these commands like this, as well:
```bash
imglyb-examples.butterfly
imglyb-examples.bdv-hello-world
imglyb-examples.bdv-painter
mglyb-examples.qt-awt
imglyb-examples.views-stack
```
