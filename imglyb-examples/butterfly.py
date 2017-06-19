from __future__ import print_function
import imglyb
from imglyb import util
from jnius import autoclass, cast
import multiprocessing
import numpy as np
from skimage import filters
from skimage import io
import time
import threading

print (imglyb)


def cast_to_rai( source ):
	return cast( 'net.imglib2.RandomAccessibleInterval', source )

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
	DistanceTransform = autoclass( 'net.imglib2.algorithm.morphology.distance.DistanceTransform' )
	DISTANCE_TYPE = autoclass( 'net.imglib2.algorithm.morphology.distance.DistanceTransform$DISTANCE_TYPE' )
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
	gradient = filters.sobel( avg )
	gradient_conv = RealARGBConverter( gradient.min(), gradient.max() )
	dt = np.zeros( avg.shape, dtype=avg.dtype )
	print( "Distance transform output mean before applying ImgLib2 dt: ", dt.mean() )
	cpu_count = multiprocessing.cpu_count()
	DistanceTransform.transform( Views.extendBorder( util.to_imglib( -gradient ) ), util.to_imglib( dt ), DISTANCE_TYPE.EUCLIDIAN, Executors.newFixedThreadPool( cpu_count ), cpu_count, 1e-2, 2e-2  )
	print( "Distance transform output mean after applying ImgLib2 dt: ", dt.mean() )
	dt_conv = RealARGBConverter( dt.min(), dt.max() )

	bdv = util.BdvFunctions.show( util.to_imglib_argb( argb ), "argb", util.options2D().frameTitle( "b-fly" ) )
	util.BdvFunctions.show( Converters.convert( cast_to_rai( util.to_imglib( avg ) ), avg_conv, t ), "mean (numpy)", util.BdvOptions.addTo( bdv ) )
	util.BdvFunctions.show( Converters.convert( cast_to_rai( util.to_imglib( gradient ) ), gradient_conv, t ), "sobel filter (scikit-imagej)", util.BdvOptions.addTo( bdv ) )
	util.BdvFunctions.show( Converters.convert( cast_to_rai( util.to_imglib( dt ) ), dt_conv, t ), "Distance Transform (ImgLib2)", util.BdvOptions.addTo( bdv ) )

	for x in range( 3 ):
		step = np.array( argb.shape ) // 3
		lower = step * x
		upper = step * ( x + 1 )
		slicing = [ slice(l,u) for l,u in zip(lower,upper)]
		rai = cast_to_rai( util.to_imglib_argb( argb[ slicing ] ) )
		util.BdvFunctions.show( Views.translate( rai, *[ int(l) for l in lower[::-1] ] ), "argb", util.BdvOptions.addTo( bdv ) )

	# Show only one source at a time.
	DisplayMode = autoclass( 'bdv.viewer.DisplayMode' )
	vp = bdv.getBdvHandle().getViewerPanel()
	grouping = vp.getVisibilityAndGrouping()
	grouping.setDisplayMode( DisplayMode.GROUP )
	for idx in range( 4 + 3 ):
		grouping.addSourceToGroup( idx, idx )

	# Keep Python running until user closes Bdv window
	check = autoclass( 'net.imglib2.python.BdvWindowClosedCheck' )()
	frame = cast( 'javax.swing.JFrame', autoclass( 'javax.swing.SwingUtilities' ).getWindowAncestor( vp ) )
	frame.addWindowListener( check )

	def sleeper():
		while check.isOpen():
			time.sleep( 0.1 )

	t = threading.Thread( target=sleeper )
	t.start()
	t.join()

