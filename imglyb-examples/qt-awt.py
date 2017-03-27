from __future__ import print_function

# THIS WORKS ON x11 only!!!
# x11: QX11EmbedContainer
# Wayland: ?
# For Cocoa: Try QMacCocoaViewContainer
# Windows: ?

# Might be possible in Qt5:
# Also: http://stackoverflow.com/questions/33699258/qt-5-5-embed-external-application-into-qwidget (qt5)

import imglyb
from imglyb import util
from jnius import autoclass, cast, PythonJavaClass, java_method
import numpy as np
from PyQt5 import QtGui, QtCore, QtWidgets
import re
import sys
import time

class MainWindow( QtWidgets.QWidget ):
	def __init__( self, bdv_frame, ndarray, viewer_panel ):
		super( MainWindow, self ).__init__()

		self.bdv_frame = bdv_frame
		self.random_button = QtWidgets.QPushButton( "QPushButton : Randomize!" )
		self.random_button2 = QtWidgets.QPushButton( "QPushButton : No op!" )
		self.random_button3 = QtWidgets.QPushButton( "QPushButton : No op!" )
		self.random_button4 = QtWidgets.QPushButton( "QPushButton : No op!" )
		self.layout = QtWidgets.QGridLayout()
		self.layout.addWidget( self.bdv_frame, 0, 0, 6, 6 )
		self.layout.addWidget( self.random_button, 0, 10, 1, 1 )
		self.layout.addWidget( self.random_button2, 1, 10, 1, 1 )
		self.layout.addWidget( self.random_button3, 2, 10, 1, 1 )
		self.layout.addWidget( self.random_button4, 3, 10, 1, 1 )
		self.layout.setContentsMargins( 0, 0, 0, 0 )
		self.setLayout( self.layout )
		self.ndarray = ndarray
		self.viewer_panel = viewer_panel

		def fill_on_click( ndarray, viewer_panel ):
			ndarray[...] = np.random.randint( 2**32, size = self.ndarray.shape )
			viewer_panel.requestRepaint()

		self.random_button.clicked.connect( lambda : fill_on_click( self.ndarray, self.viewer_panel ) )
		self.setGeometry( 300, 300, 500, 500 )

def get_parent_id_xlib( name, indent='-' ):
	from Xlib import X
	from Xlib.display import Display
	display = Display()
	root = display.screen().root
	children = root.query_tree().children
	parent_ids = []
	for c in children:
		c_name = c.get_wm_name()
		if c_name and name in c_name:
			transient_for = c.get_wm_transient_for()
			if not transient_for is None: 
				parent_ids.append( transient_for.id )

	return parent_ids

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
	# why do I need to go through 'visiblity and grouping'?
	w_ids = get_parent_id_xlib( 'visibility and grouping' )

	if len( w_ids ) == 0:
		print( "Did not find any BigDataViewer windows, exiting..." )
		sys.exit( 1 )

	elif len( w_ids ) > 1:
		print( "Found more than one BigDataViewer windows, exiting..." )
		sys.exit( 2 )
	
	print( w_ids )
	

	app = QtWidgets.QApplication( sys.argv )
	window = QtGui.QWindow.fromWinId( w_ids[0] )
	frame = QtWidgets.QWidget.createWindowContainer( window )
	mw = MainWindow( frame, img, vp )
	mw.setWindowTitle( "BigDataViewer wrapped into QT!" )
	mw.show()
	sys.exit( app.exec_() )

	
	
