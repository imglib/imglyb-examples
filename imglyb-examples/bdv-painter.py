from __future__ import print_function
import imglyb
from imglyb import util
from jnius import autoclass, cast, PythonJavaClass, java_method
import math
import numpy as np
import time
import threading

def make_sphere( num_dimensions, radius ):
	coords = [ np.arange( -radius, radius + 1 ) for d in range( num_dimensions ) ]
	mgrid = np.meshgrid( *coords )
	radius_squared = radius * radius
	return np.sum( [np.square( g ) for g in mgrid ], axis=0 ) <= radius_squared

def make_checkerboard( num_dimensions, radius ):
	coords = [ np.arange( 2 * radius ) for d in range( num_dimensions ) ]
	mgrid = np.meshgrid( *coords )
	return np.mod( np.sum( mgrid, axis=0 ), 2 ) == 0

RealPoint = autoclass( 'net.imglib2.RealPoint' )

class SpherePainter( PythonJavaClass ):
	__javainterfaces__ = ['org/scijava/ui/behaviour/DragBehaviour']


	def __init__( self, img, mask, viewer, color, paint_listener = lambda : None ):
		super( SpherePainter, self ).__init__()
		self.img = img
		self.mask = mask
		self.radius = int( mask.shape[0] / 2 )
		self.viewer = viewer
		self.color = color
		self.oX = 0
		self.oY = 0
		self.n_dim = len( img.shape )
		self.labelLocation = RealPoint( 3 )
		self.lower = np.empty( ( self.n_dim, ), dtype=np.int32 )
		self.upper = np.empty( ( self.n_dim, ), dtype=np.int32 )
		self.paint_listener = paint_listener

	@java_method('(II)V')
	def init( self, x, y ):
		self._paint( x, y )
		self.oX = x
		self.oY = y
		self.viewer.requestRepaint()
	
	@java_method('(II)V')
	def drag( self, x, y ):
		self._setCoordinates( self.oX, self.oY )
		n_dim = self.labelLocation.numDimensions()
		origin = np.array( [ self.labelLocation.getDoublePosition( d ) for d in range( n_dim ) ] )
		origin_p = RealPoint( n_dim )
		for d, p in enumerate( origin ):
			origin_p.setPosition( p, d )
		self._setCoordinates( x, y )
		target = np.array( [ self.labelLocation.getDoublePosition( d ) for d in range( n_dim ) ] )
		diff = target - origin
		length = np.linalg.norm( diff )
		direction = diff / length
		for l in range( 1, math.ceil( length ) ):
			for d, dist in enumerate( direction ):
				origin_p.move( dist, d )
			self._paint_at_localizable( origin_p )

		self.oX = x
		self.oY = y
		self.viewer.requestRepaint()
	
	@java_method('(II)V')
	def end( self, x, y ):
		self.paint_listener()

	def _paint( self, x, y ):
		self._setCoordinates( x, y )
		self._paint_at_localizable( self.labelLocation )

	def _paint_at_localizable( self, labelLocation ):
		for d in range( self.n_dim ):
			int_pos = int( round( labelLocation.getDoublePosition( d ) ) )
			if int_pos < 0 or int_pos >= self.img.shape[ d ]:
				return
			self.lower[ d ] = int_pos - self.radius
			self.upper[ d ] = int_pos + self.radius + 1


		img_lower = np.maximum( self.lower, 0 )
		img_upper = np.minimum( self.upper, self.img.shape )
		
		mask_lower = np.abs( np.minimum( self.lower, 0 ) ).astype( self.lower.dtype )
		mask_upper = np.minimum( mask_lower + ( img_upper - img_lower ), self.mask.shape )
		
		img_selection = tuple( slice(l, u) for l, u in zip( img_lower, img_upper ) )
		mask_selection = tuple( slice(l, u) for l, u in zip( mask_lower, mask_upper ) )
		
		# cropped_mask = self.mask[ mask_selection ]
		self.img[ img_selection  ][ self.mask[ mask_selection ] ] = self.color
	
	def _setCoordinates( self, x, y ):
		self.labelLocation.setPosition( x, 0 )
		self.labelLocation.setPosition( y, 1 )
		self.labelLocation.setPosition( 0, 2 )
		self.viewer.displayToGlobalCoordinates( self.labelLocation )

if __name__ == "__main__":
	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument( '--shape', '-s', default='300,200' )
	parser.add_argument( '--is2D', action='store_true' )
	parser.add_argument( '--radius', '-r', default=5, type=int )
	parser.add_argument( '--brush', '-b', default='sphere' )
	args = parser.parse_args()
	shape =  tuple( int(s) for s in args.shape.split(',') )[:4]

	brushes = {
		'sphere' : make_sphere,
		'checkers' : make_checkerboard
		}

	radius = args.radius
	mask = brushes[ args.brush ]( len(shape), radius )

	background_color = 127 << 16 | 127 << 0
	foreground_color = 229 <<  8 | 229 << 0

	img = np.empty( shape, dtype=np.int32 )
	img.fill( background_color )
	argb = util.to_imglib_argb( img )
	opts = util.options2D() if args.is2D or len(shape) == 2 else util.BdvOptions.options()
	bdv = util.BdvFunctions.show( argb, "random argbs", opts )
	vp = bdv.getBdvHandle().getViewerPanel()

# 	painter = SpherePainter( img.transpose(), mask, vp, foreground_color, lambda : print( "Foreground proportion:", np.sum( img == foreground_color ) / img.size ) )
	painter = SpherePainter( img.transpose(), mask, vp, foreground_color, lambda : None ) # print( "Now", np.sum( img == foreground_color ) / img.size, " of the image is foreground" ) )
	Helpers = autoclass( 'net.imglib2.python.Helpers' )
	behaviors = Helpers.behaviours()
	behaviors.install( bdv.getBdvHandle().getTriggerbindings(), "paint" )
	behaviors.behaviour( painter, "paint", "SPACE button1" )
	
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
	
