# -*- coding: utf-8 -*-
#system imports
import sys
# #pyqt imports
from PyQt4 import QtCore,QtGui
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QPixmap, QLabel, QMainWindow, QImage


class ImageFrame(QMainWindow):
    def __init__(self,path):
        # QtGui.QWidget.__init__(self) #初始化position
        super(ImageFrame, self).__init__()
        self.m_DragPosition=self.pos()
        screen = QtGui.QDesktopWidget().screenGeometry()
        self.resize(screen.width(), screen.height())
        self.setStyleSheet("background-color:#000000;")
        self.label = QLabel()
        self.label.setGeometry(0, 0, screen.width(), screen.height())
        self.label.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(self.label)
        img =  QImage(path)
        img = img.mirrored(True, False)
        pix = QPixmap()
        pix.convertFromImage(img)
        self.label.setPixmap(pix)
        # self.showFullScreen()

if __name__=="__main__":
    mapp=QtGui.QApplication(sys.argv)
    mw=ImageFrame()
    mw.show()
    sys.exit(mapp.exec_())