#!/usr/bin/env python

"""PyQt4 port of the layouts/basiclayout example from Qt v4.x"""

from PySide import QtCore, QtGui
import os


class Dialog(QtGui.QDialog):
    NumGridRows = 3
    NumButtons = 4

    def __init__(self):
        super(Dialog, self).__init__()

        self.imagefolder=r"E:\kuvat\137___08"
        os.chdir(self.imagefolder)
        self.folderListing=os.listdir(self.imagefolder)
        self.imageIndx=0
        print self.folderListing[self.imageIndx]
        self.createGridGroupBox()
        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(self.gridGroupBox)
        self.setLayout(mainLayout)

        self.setWindowTitle("Basic Layouts")
        self.tagitlineEdit.setFocus()



    def createGridGroupBox(self):
        self.gridGroupBox = QtGui.QGroupBox("Grid layout")
        layout = QtGui.QGridLayout()
        layout.setColumnMinimumWidth(1, 700)
        layout.setRowMinimumHeight(0, 500)
##        for i in range(Dialog.NumGridRows):
        lbutton = QtGui.QPushButton("T&aakse"  )
        layout.addWidget(lbutton, 1, 0)
        rbutton = QtGui.QPushButton("E&teen"  )
        layout.addWidget(rbutton, 1, 5)
        tagitlabel = QtGui.QLabel("Tagit" )
        self.tagitlineEdit = QtGui.QLineEdit()

        layout.addWidget(tagitlabel, 6, 0)
        layout.addWidget(self.tagitlineEdit, 6, 1)

        self.imageLabel = QtGui.QLabel()
        self.imageLabel.setBackgroundRole(QtGui.QPalette.Base)
        self.imageLabel.setSizePolicy(QtGui.QSizePolicy.Ignored,QtGui.QSizePolicy.Ignored)
##        self.imageLabel.setScaledContents(True)

##        self.smallEditor = QtGui.QTextEdit()
##        self.smallEditor.setPlainText("This widget takes up about two thirds "
##                "of the grid layout.")

        layout.addWidget(self.imageLabel, 0, 1, 4, 4)
##        layout.addWidget(self.smallEditor, 0, 1, 4, 4)

        self.infolabel = QtGui.QLabel()
        layout.addWidget(self.infolabel, 5,1,1,2)
        layout.setColumnStretch(1, 10)
        layout.setColumnStretch(2, 20)
        self.gridGroupBox.setLayout(layout)



        self.loadImg()

        rbutton.clicked.connect(self.nextImage)
        lbutton.clicked.connect(self.prevImage)


    def loadImg(self):
        fileName = self.folderListing[self.imageIndx] #r"E:\kuvat\IMG_2561.JPG"
        infotxt = "Kansio: " + self.imagefolder + "     kuva: " +fileName
        infotxt += "    " + str(self.imageIndx+1) +"/" + str( len(self.folderListing))
        self.infolabel.setText(infotxt)
        image = QtGui.QImage(fileName)
        if image.isNull():
            QtGui.QMessageBox.information(self, "Image Viewer",
                "Cannot load %s." % fileName)
            return

        self.imageLabel
        pxmap = QtGui.QPixmap.fromImage(image)
        pxmap=pxmap.scaledToHeight(500)
        self.imageLabel.setPixmap(pxmap)

##        self.scaleFactor = 0.5

    def nextImage(self):
        print "jee"
        self.imageIndx += 1
        if self.imageIndx > len(self.folderListing) -1:
            self.imageIndx = 0
        self.loadImg()
        self.tagitlineEdit.setFocus()

    def prevImage(self):
        self.imageIndx -= 1
        if self.imageIndx < 0:
            self.imageIndx = len(self.folderListing) -1

        self.loadImg()
        self.tagitlineEdit.setFocus()

if __name__ == '__main__':

    import sys

    app = QtGui.QApplication(sys.argv)
    dialog = Dialog()
    sys.exit(dialog.exec_())
