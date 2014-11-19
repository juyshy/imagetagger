#!/usr/bin/env python

"""PyQt4 port of the layouts/basiclayout example from Qt v4.x"""

from PySide import QtCore, QtGui
import os,sys,re
from datetime import datetime
##sys.path.insert(0, r'E:\python\imagetagger')
from taglistingmanager import TagListingManager

from PIL import Image

def get_date_taken(path):
    return Image.open(path)._getexif()[36867]

def loadAFile(filename):
    f = open(filename, 'r')
    loadedFileContent=f.read()
    f.close()
    return loadedFileContent

def saveFile(tiednimi,sisalto):
    f = open(tiednimi, 'w')
    f.write(sisalto)
    f.close()

class MainWindow(QtGui.QMainWindow):
    def __init__(self,taglisting):
        super(MainWindow, self).__init__()

        widget = QtGui.QWidget()
        self.setCentralWidget(widget)

        self.taglisting = taglisting
        self.taglisting.subscribe(self)

        pyappfilepath = os.path.realpath(__file__)
##        print "pyappfilepath ",pyappfilepath
        self.appDirectory = os.path.dirname(pyappfilepath)
        print "appDirectory ", self.appDirectory
        self.autoNextPic=True
        self.listSubfolders=True
        self.kuvakansio=r"E:\kuvat\137___08"
        self.readPrefs()

        os.chdir(self.kuvakansio)
        self.kuvatiedostolista=os.listdir(self.kuvakansio)

        self.indx=0
##        print self.kuvatiedostolista[self.indx]

        self.publishList=[]
        self.createActions()
        self.createMenus()
        self.createGridGroupBox()
        self.infoLabel = QtGui.QLabel(
                "<i>Choose a menu option, or right-click to invoke a context menu</i>",
                alignment=QtCore.Qt.AlignCenter)
        self.infoLabel.setFrameStyle(QtGui.QFrame.StyledPanel | QtGui.QFrame.Sunken)

        mainLayout = QtGui.QVBoxLayout()
##        mainLayout.setMenuBar(self.menuBar)
        mainLayout.addWidget(self.infoLabel)
        mainLayout.addWidget(self.gridGroupBox)
##        self.setLayout(mainLayout)
        widget.setLayout(mainLayout)
        self.setWindowTitle("ImageTagger")
        self.tagitlineEdit.setFocus()
        self.indx=self.jumpToEmpty()
        self.loadImg()

    def readPrefs(self):
        prefs=loadAFile(".prefs")
        prefsLines = prefs.split("\n")
        prefsHash={}
        for prfline in prefsLines:
            prfkeyvaluepair= prfline.split("=")
            prefsHash[prfkeyvaluepair[0]]=prfkeyvaluepair[1]

        self.autoNextPic= prefsHash["autoNextPic"]== "True"
        self.listSubfolders=prefsHash["listSubfolders"]== "True"
        self.kuvakansio=prefsHash["kuvakansio"]
        print self.autoNextPic
        print self.listSubfolders
        print self.kuvakansio

    def createActions(self):
        self.newAct = QtGui.QAction("&New taglisting", self,
                shortcut=QtGui.QKeySequence.New,
                statusTip="Create a new taglisting", triggered=self.newFile)

        self.openAct = QtGui.QAction("&Open taglisting", self,
                shortcut=QtGui.QKeySequence.Open,
                statusTip="Open a taglisting", triggered=self.open)

        self.saveAct = QtGui.QAction("&Save taglisting", self,
                shortcut=QtGui.QKeySequence.Save,
                statusTip="Save taglisting", triggered=self.save)

        self.chooseFolderAct = QtGui.QAction("&Choose Image folder", self,
                shortcut=QtGui.QKeySequence(QtCore.Qt.CTRL + QtCore.Qt.Key_L),
                statusTip="Choose Image folder", triggered=self.chooseFolder)

        self.printAct = QtGui.QAction("&Print...", self,
                shortcut=QtGui.QKeySequence.Print,
                statusTip="Print the document", triggered=self.print_)

        self.exitAct = QtGui.QAction("E&xit", self, shortcut="Ctrl+Q",
                statusTip="Exit the application", triggered=self.close)

        self.jumpToIndexAct = QtGui.QAction("&Jump To Index", self,
                shortcut=QtGui.QKeySequence("Ctrl+J"),
                statusTip="Jump to index", triggered=self.jumpToIndex)

        self.showPublishListAct = QtGui.QAction("&Show Publish List", self,
                shortcut=QtGui.QKeySequence("Ctrl+U"),
                statusTip="Show Publish List", triggered=self.showPublishList)

        self.savePubListAct   = QtGui.QAction("&Save Publish List", self,
                shortcut=QtGui.QKeySequence("Ctrl+Alt+S"),
                statusTip="Show Publish List", triggered=self.savePubList)

        self.clearPubListAct = QtGui.QAction("&Clear Publish List", self,
                shortcut=QtGui.QKeySequence("Ctrl+Alt+C"),
                statusTip="Clear Publish List", triggered=self.clearPubList)

        self.undoAct = QtGui.QAction("&Undo", self,
                shortcut=QtGui.QKeySequence.Undo,
                statusTip="Undo the last operation", triggered=self.undo)

        self.redoAct = QtGui.QAction("&Redo", self,
                shortcut=QtGui.QKeySequence.Redo,
                statusTip="Redo the last operation", triggered=self.redo)

        self.cutAct = QtGui.QAction("Cu&t", self,
                shortcut=QtGui.QKeySequence.Cut,
                statusTip="Cut the current selection's contents to the clipboard",
                triggered=self.cut)

        self.copyAct = QtGui.QAction("&Copy", self,
                shortcut=QtGui.QKeySequence.Copy,
                statusTip="Copy the current selection's contents to the clipboard",
                triggered=self.copy)

        self.pasteAct = QtGui.QAction("&Paste", self,
                shortcut=QtGui.QKeySequence.Paste,
                statusTip="Paste the clipboard's contents into the current selection",
                triggered=self.paste)

        self.boldAct = QtGui.QAction("&Bold", self, checkable=True,
                shortcut="Ctrl+B", statusTip="Make the text bold",
                triggered=self.bold)

        boldFont = self.boldAct.font()
        boldFont.setBold(True)
        self.boldAct.setFont(boldFont)

        self.italicAct = QtGui.QAction("&Italic", self, checkable=True,
                shortcut="Ctrl+I", statusTip="Make the text italic",
                triggered=self.italic)

        italicFont = self.italicAct.font()
        italicFont.setItalic(True)
        self.italicAct.setFont(italicFont)

        self.setLineSpacingAct = QtGui.QAction("Set &Line Spacing...", self,
                statusTip="Change the gap between the lines of a paragraph",
                triggered=self.setLineSpacing)

        self.setParagraphSpacingAct = QtGui.QAction(
                "Set &Paragraph Spacing...", self,
                statusTip="Change the gap between paragraphs",
                triggered=self.setParagraphSpacing)

        self.aboutAct = QtGui.QAction("&About", self,
                statusTip="Show the application's About box",
                triggered=self.about)

        self.aboutQtAct = QtGui.QAction("About &Qt", self,
                statusTip="Show the Qt library's About box",
                triggered=self.aboutQt)
        self.aboutQtAct.triggered.connect(QtGui.qApp.aboutQt)

        self.leftAlignAct = QtGui.QAction("&Left Align", self, checkable=True,
                shortcut="Ctrl+L", statusTip="Left align the selected text",
                triggered=self.leftAlign)

        self.rightAlignAct = QtGui.QAction("&Right Align", self,
                checkable=True, shortcut="Ctrl+R",
                statusTip="Right align the selected text",
                triggered=self.rightAlign)

        self.justifyAct = QtGui.QAction("&Justify", self, checkable=True,
                shortcut="Ctrl+J", statusTip="Justify the selected text",
                triggered=self.justify)

        self.centerAct = QtGui.QAction("&Center", self, checkable=True,
                shortcut="Ctrl+C", statusTip="Center the selected text",
                triggered=self.center)

        self.alignmentGroup = QtGui.QActionGroup(self)
        self.alignmentGroup.addAction(self.leftAlignAct)
        self.alignmentGroup.addAction(self.rightAlignAct)
        self.alignmentGroup.addAction(self.justifyAct)
        self.alignmentGroup.addAction(self.centerAct)
        self.leftAlignAct.setChecked(True)

    def createMenus(self):
        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenu.addAction(self.newAct)
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addAction(self.saveAct)
        self.fileMenu.addAction(self.chooseFolderAct)

        self.fileMenu.addAction(self.printAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAct)

        self.editMenu = self.menuBar().addMenu("&Edit")
        self.editMenu.addAction(self.undoAct)
        self.editMenu.addAction(self.redoAct)
        self.editMenu.addSeparator()
        self.editMenu.addAction(self.cutAct)
        self.editMenu.addAction(self.copyAct)
        self.editMenu.addAction(self.pasteAct)
        self.editMenu.addSeparator()

        self.imagesMenu = self.menuBar().addMenu("&Images")
        self.imagesMenu.addAction(self.jumpToIndexAct)

        self.publishMenu = self.menuBar().addMenu("&Publish")
        self.publishMenu.addAction(self.showPublishListAct)
        self.publishMenu.addAction(self.savePubListAct)
        self.publishMenu.addAction(self.clearPubListAct)


        self.helpMenu = self.menuBar().addMenu("&Help")
        self.helpMenu.addAction(self.aboutAct)
        self.helpMenu.addAction(self.aboutQtAct)

##        self.formatMenu = self.editMenu.addMenu("&Format")
##        self.formatMenu.addAction(self.boldAct)
##        self.formatMenu.addAction(self.italicAct)
##        self.formatMenu.addSeparator().setText("Alignment")
##        self.formatMenu.addAction(self.leftAlignAct)
##        self.formatMenu.addAction(self.rightAlignAct)
##        self.formatMenu.addAction(self.justifyAct)
##        self.formatMenu.addAction(self.centerAct)
##        self.formatMenu.addSeparator()
##        self.formatMenu.addAction(self.setLineSpacingAct)
##        self.formatMenu.addAction(self.setParagraphSpacingAct)

    def setExistingDirectory(self):
        options = QtGui.QFileDialog.DontResolveSymlinks | QtGui.QFileDialog.ShowDirsOnly
        directory = QtGui.QFileDialog.getExistingDirectory(self,
                "QFileDialog.getExistingDirectory()",
                self.directoryLabel.text(), options)
        if directory:
            self.directoryLabel.setText(directory)

    def newFile(self):
        self.infoLabel.setText("Invoked <b>File|New</b>")

    def open(self):
        self.infoLabel.setText("Invoked <b>File|Open</b>")

    def save(self):
        self.infoLabel.setText("Invoked <b>File|Save</b>")

    def chooseFolder(self):
        self.setExistingDirectory()
        self.infoLabel.setText("Invoked <b>File|chooseFolder</b>")

    def print_(self):
        self.infoLabel.setText("Invoked <b>File|Print</b>")

    def undo(self):
        self.infoLabel.setText("Invoked <b>Edit|Undo</b>")

    def jumpToIndex(self):
        self.infoLabel.setText("Invoked <b>jump To Index</b>")

    def showPublishList(self):
        self.infoLabel.setText("Invoked <b>Show Publish List</b>")
        print self.publishList

    def savePubList(self):
        self.infoLabel.setText("Invoked <b>Save Publish List</b>")
        list2save= self.kuvakansio + "\n" + "\n".join(self.publishList)
        tiednimi = self.appDirectory + "/" + "publishlist_" + "{0:%d-%m-%Y-%H-%M-%S}".format(datetime.now()) + ".txt"
        saveFile(tiednimi, list2save)

    def clearPubList(self):
        self.infoLabel.setText("Invoked <b>Clear Publish List</b>")
        self.publishList =[]

    def redo(self):
        self.infoLabel.setText("Invoked <b>Edit|Redo</b>")

    def cut(self):
        self.infoLabel.setText("Invoked <b>Edit|Cut</b>")

    def copy(self):
        self.infoLabel.setText("Invoked <b>Edit|Copy</b>")

    def paste(self):
        self.infoLabel.setText("Invoked <b>Edit|Paste</b>")

    def bold(self):
        self.infoLabel.setText("Invoked <b>Edit|Format|Bold</b>")

    def italic(self):
        self.infoLabel.setText("Invoked <b>Edit|Format|Italic</b>")

    def leftAlign(self):
        self.infoLabel.setText("Invoked <b>Edit|Format|Left Align</b>")

    def rightAlign(self):
        self.infoLabel.setText("Invoked <b>Edit|Format|Right Align</b>")

    def justify(self):
        self.infoLabel.setText("Invoked <b>Edit|Format|Justify</b>")

    def center(self):
        self.infoLabel.setText("Invoked <b>Edit|Format|Center</b>")

    def setLineSpacing(self):
        self.infoLabel.setText("Invoked <b>Edit|Format|Set Line Spacing</b>")

    def setParagraphSpacing(self):
        self.infoLabel.setText("Invoked <b>Edit|Format|Set Paragraph Spacing</b>")

    def about(self):
        self.infoLabel.setText("Invoked <b>Help|About</b>")
        QtGui.QMessageBox.about(self, "About Menu",
                "The <b>Menu</b> example shows how to create menu-bar menus "
                "and context menus.")

    def aboutQt(self):
        self.infoLabel.setText("Invoked <b>Help|About Qt</b>")

    def keyPressEvent(self, event):

        if event.key() == QtCore.Qt.Key_Right:
            print "OIKEANUOLI"
             #) - (event.key() == QtCore.Qt.Key_Left)) % self.width

    def createGridGroupBox(self):
        self.gridGroupBox = QtGui.QGroupBox("Grid layout")
        layout = QtGui.QGridLayout()
        layout.setColumnMinimumWidth(1, 700)
        layout.setRowMinimumHeight(0, 500)
##        for i in range(Dialog.NumGridRows):

        flkrbutton = QtGui.QPushButton("P&ublish"  )
        flkrbutton.setFocusPolicy(QtCore.Qt.NoFocus)
        layout.addWidget(flkrbutton, 1, 0)

        lbutton = QtGui.QPushButton("P&revious"  )
        lbutton.setFocusPolicy(QtCore.Qt.NoFocus)
        layout.addWidget(lbutton, 2, 0)
        rbutton = QtGui.QPushButton("Nex&t"  )
        rbutton.setFocusPolicy(QtCore.Qt.NoFocus)
        layout.addWidget(rbutton, 2, 5)
        tagitlabel = QtGui.QLabel("Tagit" )
        self.tagitlineEdit = QtGui.QLineEdit()


        self.tagitlineEdit.returnPressed.connect(self._lineedit_returnPressed)

        layout.addWidget(tagitlabel, 7, 0)
        layout.addWidget(self.tagitlineEdit, 7, 1)

        self.imageLabel = QtGui.QLabel()
        self.imageLabel.setBackgroundRole(QtGui.QPalette.Base)
        self.imageLabel.setSizePolicy(QtGui.QSizePolicy.Ignored,QtGui.QSizePolicy.Ignored)

        frameStyle = QtGui.QFrame.Sunken | QtGui.QFrame.Panel
        self.directoryLabel = QtGui.QLabel()
        self.directoryLabel.setFrameStyle(frameStyle)
        layout.addWidget(self.directoryLabel, 8, 1)
##        self.imageLabel.setScaledContents(True)

##        self.smallEditor = QtGui.QTextEdit()
##        self.smallEditor.setPlainText("This widget takes up about two thirds "
##                "of the grid layout.")

        layout.addWidget(self.imageLabel, 0, 1, 5, 4)
##        layout.addWidget(self.smallEditor, 0, 1, 4, 4)

        self.infolabel = QtGui.QLabel()
        layout.addWidget(self.infolabel, 6,1,1,2)
        layout.setColumnStretch(1, 10)
        layout.setColumnStretch(2, 20)
        self.gridGroupBox.setLayout(layout)

##        self.loadImg()

        rbutton.clicked.connect(self.nextImage)
        lbutton.clicked.connect(self.prevImage)
        flkrbutton.clicked.connect(self.addToPublishList)
##        wordList = ["alpha", "omega", "omicron", "zeta"]
        self.setCompleterList()

    def jumpToEmpty(self):
        self.tagattyLukumaara=0
        for i, kuva in enumerate( self.kuvatiedostolista):
            if kuva in self.taglisting.kuvatHash.keys():
                self.tagattyLukumaara +=1
        if self.tagattyLukumaara < len(self.kuvatiedostolista):
            for i, kuva in enumerate( self.kuvatiedostolista):
                if kuva not in self.taglisting.kuvatHash.keys():
                    break
            return i
        else:
            return 0

    def setCompleterList(self):
        tageiar=[]
        for tagii in self.taglisting.kuvatHash.values():
            try:
                tagiar= re.split(r'[, ]', tagii.decode("utf-8"))
                tageiar.append(tagii.decode("utf-8"))
            except:
                tagiar= re.split(r'[, ]', tagii )
                tageiar.append(tagii )
            tagiar2=[tg.strip() for tg in tagiar if tg.strip() !=""]
            tageiar += tagiar2

        tageiarunq=list( set( tageiar))
##        print tageiar
        self.setCompleterValues(tageiarunq)

    def tiedostonLastMod(self,tiedosto):
##        tiedosto=r"E:\kuvat\137___08\IMG_3773.JPG"

        return "{0:%d.%m.%Y %H:%M:%S}".format(datetime.fromtimestamp(os.stat(tiedosto).st_mtime))

##        print    os.stat(tiedosto).st_mtime
##         print datetime.fromtimestamp(os.stat(tiedosto).st_mtime)

##        get_date_taken(tiedosto)

    def setCompleterValues(self,wordList):

        completer = QtGui.QCompleter(wordList, self)
        completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.tagitlineEdit.setCompleter(completer)

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
        self.lastTagi=self.tagitlineEdit.text()
        self.setCompleterList()
        self.tagitlineEdit.setText( self.lastTagi)
        if self.autoNextPic:
            self.nextImage()


    def loadImg(self):
        fileName = self.kuvatiedostolista[self.indx] #r"E:\kuvat\IMG_2561.JPG"
        infotxt = "Kansio: " + self.kuvakansio + "     kuva: " +fileName
        infotxt += "    " + str(self.indx+1) +"/" + str( len(self.kuvatiedostolista))
        infotxt += "    otettu: " +  get_date_taken(fileName)
        infotxt += "    tagatty: " +  str(self.tagattyLukumaara) +"/" + str( len(self.kuvatiedostolista))
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
        pxmap=pxmap.scaledToHeight(600)
        if self.kuvatiedostolista[self.indx] in self.taglisting.kuvatHash.keys() :  #jos kuva on jo luettelossa
            self.tagitlineEdit.setText( self.taglisting.kuvatHash[self.kuvatiedostolista[self.indx]].decode("utf-8"))
##        else:
##            self.tagitlineEdit.setText("")
        self.imageLabel.setPixmap(pxmap)

##        self.scaleFactor = 0.5

    def nextImage(self):
##        print "jee"
        if self.kuvatiedostolista != []:
            self.indx += 1
            if self.indx > len(self.kuvatiedostolista) -1:
                self.indx = 0
            self.loadImg()
            self.tagitlineEdit.setFocus()
            self.tagitlineEdit.selectAll()

    def prevImage(self):
        if self.kuvatiedostolista != []:
            self.indx -= 1
            if self.indx < 0:
                self.indx = len(self.kuvatiedostolista) -1

            self.loadImg()
            self.tagitlineEdit.setFocus()
            self.tagitlineEdit.selectAll()

    def addToPublishList(self):
        self.publishList.append(self.kuvatiedostolista[self.indx])
        print "added: ",self.kuvatiedostolista[self.indx]


if __name__ == '__main__':

    import sys

    app = QtGui.QApplication(sys.argv)
    ohjelmapath=r"E:\python\imagetagger"
    tagilistMangr= TagListingManager(ohjelmapath)
##    dialog = Dialog(tagilistMangr)
    window = MainWindow(tagilistMangr)

    window.show()


    sys.exit(app.exec_())
