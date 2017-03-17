from __future__ import print_function
import imglyb
from imglyb import util
from jnius import autoclass, cast
import multiprocessing
import numpy as np
from skimage import io
import time
import vigra

print (imglyb)

if __name__ == "__main__":
	import argparse
	default_url = 'https://github.com/hanslovsky/imglyb-examples/raw/master/resources/butterfly_small.jpg'

	parser = argparse.ArgumentParser()
	parser.add_argument( '--url', '-u', default=default_url )

	args = parser.parse_args()

	RealARGBConverter = autoclass( 'net.imglib2.converter.RealARGBConverter')
	Converters = autoclass( 'net.imglib2.converter.Converters' )
	ARGBType = autoclass ( 'net.imglib2.type.numeric.ARGBType' )
	RealType = autoclass ( 'net.imglib2.type.numeric.real.DoubleType' )
	DifferenceOfGaussian = autoclass( 'net.imglib2.algorithm.dog.DifferenceOfGaussian' )
	Views = autoclass( 'net.imglib2.view.Views' )
	Executors = autoclass( 'java.util.concurrent.Executors' )
	t = ARGBType()

	img = io.imread( args.url )
	argb = (
		np.left_shift(img[...,0], np.zeros(img.shape[:-1],dtype=np.uint32) + 16) + \
		np.left_shift(img[...,1], np.zeros(img.shape[:-1],dtype=np.uint32) + 8)  + \
		np.left_shift(img[...,2], np.zeros(img.shape[:-1],dtype=np.uint32) + 0) ) \
		.astype( np.int32 )

	avg = np.mean( img, axis=2 )
	avg_conv = RealARGBConverter( avg.min(), avg.max() )

	gradient = vigra.filters.gaussianGradientMagnitude( avg, 5.0 )
	gradient_conv = RealARGBConverter( gradient.min(), gradient.max() )

	dog = np.zeros( avg.shape, dtype=avg.dtype )
	print( "DoG output mean before applying ImgLib2 DoG: ", dog.mean() )
	DifferenceOfGaussian.DoG(
		[2.0, 2.0],
		[5.0, 5.0],
		Views.extendBorder( util.to_imglib( avg ) ),
		util.to_imglib( dog ),
		Executors.newFixedThreadPool( multiprocessing.cpu_count() * 3 )
		)
	print( "DoG output mean after before applying ImgLib2 DoG: ", dog.mean() )
	dog_conv = RealARGBConverter( dog.min(), dog.max() )
	

	bdv = util.BdvFunctions.show( util.to_imglib_argb( argb ), "argb", util.options2D() )
	util.BdvFunctions.show( Converters.convert( util.to_imglib( avg ), avg_conv, t ), "mean (numpy)", util.BdvOptions.addTo( bdv ) )
	util.BdvFunctions.show( Converters.convert( util.to_imglib( gradient ), gradient_conv, t ), "gradient (vigra)", util.BdvOptions.addTo( bdv ) )
	util.BdvFunctions.show( Converters.convert( util.to_imglib( dog ), dog_conv, t ), "DoG (ImgLib2)", util.BdvOptions.addTo( bdv ) )

	# Show only one source at a time.
	DisplayMode = autoclass( 'bdv.viewer.DisplayMode' )
	vp = bdv.getBdvHandle().getViewerPanel()
	grouping = vp.getVisibilityAndGrouping()
	grouping.setDisplayMode( DisplayMode.GROUP )
	for idx in range(4):
		grouping.addSourceToGroup( idx, idx )

	# Keep Python running until user closes Bdv window
	check = autoclass( 'net.imglib2.python.BdvWindowClosedCheck' )()
	frame = cast( 'javax.swing.JFrame', autoclass( 'javax.swing.SwingUtilities' ).getWindowAncestor( vp ) )
	frame.addWindowListener( check )
	while check.isOpen():
		time.sleep( 0.1 )

