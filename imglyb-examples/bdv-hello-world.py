from __future__ import print_function
import imglyb
from imglyb import util
from jnius import autoclass, cast, PythonJavaClass, java_method
import numpy as np
import time
import threading

print (imglyb)


class RectangleOverlayRenderer:
	def __init__( self ):
		self.w = 0
		self.h = 0
		self.color= autoclass('java.awt.Color').WHITE
		self.stroke = autoclass('java.awt.BasicStroke')( 10 )

	def draw_overlays( self, g ):
		g2d = cast('java.awt.Graphics2D', g)
		g2d.setColor( self.color )
		g2d.setStroke( self.stroke )
		g2d.drawRect( self.w // 2 - self.w // 6, self.h // 2 - self.h // 6, self.w // 3, self.h // 3 )

	def set_canvas_size( self, width, height ):
		print( "Setting canvas size", width, height )
		self.w = width
		self.h = height


if __name__ == "__main__":
	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument( '--shape', '-s', default='300,200' )
	parser.add_argument( '--is2D', action='store_true' )
	args = parser.parse_args()
	shape =  tuple( int(s) for s in args.shape.split(',') )[:4]
	
	coordinate_printer = util.GenericMouseMotionListener(
		lambda e : None,
		lambda e : print( "mouse moved", e.getX(), e.getY() )
		)

	hello_world_color= autoclass('java.awt.Color').WHITE
	def hello_world( g ):
		g2d = cast('java.awt.Graphics2D', g)
		g2d.setColor( hello_world_color )
		g2d.drawString("Hello world!", 30, 130 )
	hello_world_overlay = util.GenericOverlayRenderer(
		hello_world 
		)

	renderer_helper = RectangleOverlayRenderer()
	rectangle_renderer = util.GenericOverlayRenderer( lambda g : renderer_helper.draw_overlays( g ), lambda w, h : renderer_helper.set_canvas_size( w, h ) )

	img = np.random.randint( 2**32, size=shape ).astype( np.uint32 )
	argb = util.to_imglib_argb( img )

	opts = util.options2D() if args.is2D or len(shape) == 2 else util.BdvOptions.options()
	bdv = util.BdvFunctions.show( argb, "random argbs", opts )
	vp = bdv.getBdvHandle().getViewerPanel()
	vp.getDisplay().addMouseMotionListener( coordinate_printer )
	vp.getDisplay().addOverlayRenderer( hello_world_overlay )
	vp.getDisplay().addOverlayRenderer( rectangle_renderer )

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
