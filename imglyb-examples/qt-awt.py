from __future__ import print_function

# THIS WORKS ON x11 only!!!

import imglyb
from imglyb import util
from jnius import autoclass, cast, PythonJavaClass, java_method
import numpy as np
from PyQt4 import QtGui, QtCore
import re
import subprocess
import sys
import time

class MainWindow( QtGui.QWidget ):
	def __init__( self, bdv_frame, ndarray, viewer_panel ):
		super( MainWindow, self ).__init__()

		self.bdv_frame = bdv_frame
		self.random_button = QtGui.QPushButton( "QPushButton : Randomize!" )
		self.layout = QtGui.QVBoxLayout()
		self.layout.addWidget( self.bdv_frame )
		self.layout.addWidget( self.random_button )
		self.setLayout( self.layout )
		self.ndarray = ndarray
		self.viewer_panel = viewer_panel

		def fill_on_click( ndarray, viewer_panel ):
			ndarray[...] = np.random.randint( 2**32, size = self.ndarray.shape )
			viewer_panel.requestRepaint()

		self.random_button.clicked.connect( lambda : fill_on_click( self.ndarray, self.viewer_panel ) )


if __name__ == "__main__":
	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument( '--width', '-W', type=int, default=400 )
	parser.add_argument( '--height', '-H', type=int, default=300 )
	parser.add_argument( '--n-slices', '-N', type=int, default=200 )

	args = parser.parse_args()

	img = np.zeros( (args.n_slices, args.height, args.width ), dtype=np.uint32 ) + 255
		
	bdv = util.BdvFunctions.show( util.to_imglib_argb( img ), 'stack' )
	vp = bdv.getBdvHandle().getViewerPanel()

	# Keep Python running until user closes Bdv window
	check = autoclass( 'net.imglib2.python.BdvWindowClosedCheck' )()
	frame = cast( 'javax.swing.JFrame', autoclass( 'javax.swing.SwingUtilities' ).getWindowAncestor( vp ) )
	frame.addWindowListener( check )

	cmd = [ 'xwininfo', '-name', 'BigDataViewer' ] #  | grep -oP '(?<=id: )(0x[0-9]+)'"
	
	xwininfo = subprocess.Popen( cmd, stdout=subprocess.PIPE )
	out, err = xwininfo.communicate()
	w_ids = [ l for l in str( out ).split( '\\n' ) if 'Window id' in l ]

	if len( w_ids ) == 0:
		print( "Did not find any BigDataViewer windows, exiting..." )
		sys.exit( 1 )

	elif len( w_ids ) > 1:
		print( "Found more than one BigDataViewer windows, exiting..." )
		sys.exit( 2 )
	
	w_ids = [ re.search( '(0x[0-9A-Za-z]+)', w_id ).group( 1 ) for w_id in w_ids ]
	
	
	app = QtGui.QApplication( sys.argv )
	frame = QtGui.QX11EmbedContainer()
	mw = MainWindow( frame, img, vp )
	frame.embedClient( int( w_ids[0], 16 ) )
	mw.show()
	sys.exit( app.exec_() )

	
	
