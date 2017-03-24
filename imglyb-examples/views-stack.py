import imglyb
from imglyb import util
from jnius import autoclass, cast
import numpy as np
import time

if __name__ == "__main__":
	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument( '--width', '-W', type=int, default=400 )
	parser.add_argument( '--height', '-H', type=int, default=300 )
	parser.add_argument( '--n-slices', '-N', type=int, default=200 )

	args = parser.parse_args()
	norm = 2**16 * 1.0 / ( args.width * args.height + args.n_slices )

	XX, YY = np.meshgrid( np.arange( args.height ), np.arange( args.width ) )
	vals = XX * YY

	imgs = [ z + vals * norm for z in range( args.n_slices ) ]

	ArrayList = autoclass( 'java.util.ArrayList' )
	slices = ArrayList()
	for i in imgs:
		slices.add( util.to_imglib( i ) )

	stack = util.Views.stack( slices )
		
	bdv = util.BdvFunctions.show( stack, 'stack' )
	vp = bdv.getBdvHandle().getViewerPanel()
	print ( [(i.min(), i.max()) for i in imgs] )

	# Keep Python running until user closes Bdv window
	check = autoclass( 'net.imglib2.python.BdvWindowClosedCheck' )()
	frame = cast( 'javax.swing.JFrame', autoclass( 'javax.swing.SwingUtilities' ).getWindowAncestor( vp ) )
	frame.addWindowListener( check )
	while check.isOpen():
		time.sleep( 0.1 )
	
