from __future__ import print_function
import imglyb
from imglyb import util
from jnius import autoclass, cast, PythonJavaClass, java_method
import numpy as np
import time

def make_sphere( num_dimensions, radius ):
	coords = [ np.arange( -radius, radius + 1 ) for d in range( num_dimensions ) ]
	mgrid = np.meshgrid( *coords )
	radius_squared = radius * radius
	return np.sum( [np.square( g ) for g in mgrid ], axis=0 ) <= radius_squared

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
		self.labelLocation = autoclass('net.imglib2.RealPoint')( 3 )
		self.lower = np.empty( ( self.n_dim, ), dtype=np.int32 )
		self.upper = np.empty( ( self.n_dim, ), dtype=np.int32 )
		self.paint_listener = paint_listener

	@java_method('(II)V')
	def init( self, x, y ):
		self._paint( x, y )
	
	@java_method('(II)V')
	def drag( self, x, y ):
		self._paint( x, y )
	
	@java_method('(II)V')
	def end( self, x, y ):
		pass

	def _paint( self, x, y ):
		self._setCoordinates( x, y )
		for d in range( self.n_dim ):
			int_pos = int( round( self.labelLocation.getDoublePosition( d ) ) )
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
		self.paint_listener()
		self.viewer.requestRepaint()
	
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
	args = parser.parse_args()
	shape =  tuple( int(s) for s in args.shape.split(',') )[:4]

	radius = args.radius
	mask = make_sphere( len(shape), radius )

	background_color = 127 << 16 | 127 << 0
	foreground_color = 229 <<  8 | 229 << 0

	img = np.empty( shape, dtype=np.int32 )
	img.fill( background_color )
	argb = util.to_imglib_argb( img )
	opts = util.options2D() if args.is2D or len(shape) == 2 else util.BdvOptions.options()
	bdv = util.BdvFunctions.show( argb, "random argbs", opts )
	vp = bdv.getBdvHandle().getViewerPanel()

	painter = SpherePainter( img.transpose(), mask, vp, foreground_color, lambda : print( "Now", np.sum( img == foreground_color ) / img.size, " of the image is foreground" ) )
	Helpers = autoclass( 'net.imglib2.python.Helpers' )
	behaviors = Helpers.behaviours()
	behaviors.install( bdv.getBdvHandle().getTriggerbindings(), "paint" )
	behaviors.behaviour( painter, "paint", "SPACE button1" )
	
	# Keep Python running until user closes Bdv window
	check = autoclass( 'net.imglib2.python.BdvWindowClosedCheck' )()
	frame = cast( 'javax.swing.JFrame', autoclass( 'javax.swing.SwingUtilities' ).getWindowAncestor( vp ) )
	frame.addWindowListener( check )
	while check.isOpen():
		time.sleep( 0.1 )
