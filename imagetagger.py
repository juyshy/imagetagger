#!/usr/bin/env python

"""PyQt4 port of the layouts/basiclayout example from Qt v4.x"""

from PySide import QtCore, QtGui
import os,sys
from datetime import datetime
sys.path.insert(0, r'E:\python\imagetagger')
from taglistingmanager import TagListingManager

from PIL import Image
def get_date_taken(path):
    return Image.open(path)._getexif()[36867]

class Dialog(QtGui.QDialog):
    NumGridRows = 3
    NumButtons = 4

    def __init__(self,taglisting):
        super(Dialog, self).__init__()


        self.taglisting = taglisting
        self.taglisting.subscribe(self)
        self.autoNextPic=True
        self.kuvakansio=r"E:\kuvat\137___08"
        os.chdir(self.kuvakansio)
        self.kuvatiedostolista=os.listdir(self.kuvakansio)
        self.indx=0
        print self.kuvatiedostolista[self.indx]
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
        lbutton.setFocusPolicy(QtCore.Qt.NoFocus)
        layout.addWidget(lbutton, 1, 0)
        rbutton = QtGui.QPushButton("E&teen"  )
        rbutton.setFocusPolicy(QtCore.Qt.NoFocus)
        layout.addWidget(rbutton, 1, 5)
        tagitlabel = QtGui.QLabel("Tagit" )
        self.tagitlineEdit = QtGui.QLineEdit()
        self.tagitlineEdit.returnPressed.connect(self._lineedit_returnPressed)

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

    def tiedostonLastMod(self,tiedosto):
##        tiedosto=r"E:\kuvat\137___08\IMG_3773.JPG"

        return "{0:%d.%m.%Y %H:%M:%S}".format(datetime.fromtimestamp(os.stat(tiedosto).st_mtime))

##        print    os.stat(tiedosto).st_mtime
##         print datetime.fromtimestamp(os.stat(tiedosto).st_mtime)

        get_date_taken(tiedosto)

    def _lineedit_returnPressed(self):
        print "text:", self.tagitlineEdit.text()
        tiedosto = self.kuvatiedostolista[self.indx]
        print tiedosto
        date_taken = get_date_taken(tiedosto)
        print date_taken
        time =  self.tiedostonLastMod(tiedosto)
        print time
        koko = str(os.stat(tiedosto).st_size  / 1000 ) + "kb"
        koko
        tagirivi = self.kuvatiedostolista[self.indx]+" | "+ self.tagitlineEdit.text() +" | "+ date_taken + " " + time+" "+self.pixkoko+" "+koko+" | "

        timenowstr= "{0:%d.%m.%Y %H:%M:%S}".format(datetime.now())
        tagirivi += self.kuvakansio +" | tagd: " + timenowstr + "\n"
        print tagirivi
        self.taglisting.lisaaTagi(self.tagitlineEdit.text(), tagirivi)
        if self.autoNextPic:
            self.nextImage()

    def loadImg(self):
        fileName = self.kuvatiedostolista[self.indx] #r"E:\kuvat\IMG_2561.JPG"
        infotxt = "Kansio: " + self.kuvakansio + "     kuva: " +fileName
        infotxt += "    " + str(self.indx+1) +"/" + str( len(self.kuvatiedostolista))
        self.infolabel.setText(infotxt)
        image = QtGui.QImage(fileName)
        if image.isNull():
            QtGui.QMessageBox.information(self, "Image Viewer",
                "Cannot load %s." % fileName)
            return

##        self.imageLabel
        size = image.size()
        pixkokoz=size.width(), size.height()
        self.pixkoko= str(pixkokoz[0])+"X"+str(pixkokoz[1])
        pxmap = QtGui.QPixmap.fromImage(image)
        pxmap=pxmap.scaledToHeight(500)
        self.imageLabel.setPixmap(pxmap)

##        self.scaleFactor = 0.5

    def nextImage(self):
##        print "jee"
        self.indx += 1
        if self.indx > len(self.kuvatiedostolista) -1:
            self.indx = 0
        self.loadImg()
        self.tagitlineEdit.setFocus()

    def prevImage(self):
        self.indx -= 1
        if self.indx < 0:
            self.indx = len(self.kuvatiedostolista) -1

        self.loadImg()
        self.tagitlineEdit.setFocus()

if __name__ == '__main__':

    import sys

    app = QtGui.QApplication(sys.argv)
    ohjelmapath=r"E:\python\imagetagger"
    tagilistMangr= TagListingManager(ohjelmapath)
    dialog = Dialog(tagilistMangr)

    sys.exit(dialog.exec_())
