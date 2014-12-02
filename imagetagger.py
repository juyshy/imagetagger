#!/usr/bin/env python

"""PyQt4 port of the layouts/basiclayout example from Qt v4.x"""

from PySide import QtCore, QtGui
import shutil
import os,sys,re
from datetime import datetime
##sys.path.insert(0, r'E:\python\imagetagger')
from taglistingmanager import TagListingManager
import subprocess
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

def getVolSerial():
    batcmd = "dir"
    cmdinfo = subprocess.check_output(batcmd, shell=True)
##    print cmdinfo[:130]
    hdvolserial =re.findall(r'Volume Serial Number is (.*?)\r\n', cmdinfo[:130])[0]
    return hdvolserial


class ImageInfo(object):
    def __init__(self,filename,infosource = 'harddrive'):
        self.filename = filename #os.path.dirname(fullpath)
        self.fullpath = None
        self.folderpath = None # os.path.dirname(fullpath)
        self.size = None
        self.lastmodified= None
        self.pictaken= None
        self.tags= None
        self.title= None
        self.pubtags= None
        self.pixsize= None
        self.volserial = None
        self.taggedtime = None
        self.unsharp = False
        self.pendingdelete = False
        self.infosource = infosource

        if  self.infosource == 'harddrive':
            self.scanMetadata()


        def scanMetadata(self):
            try:
                self.size=os.path.getsize(self.fullpath )
            except:
                pass
            try:
                self.lastmodified=os.path.getmtime(self.fullpath )
            except:
                pass
            try:
                self.pictaken =  get_date_taken(path)
            except:
                pass



class HoverLabel(QtGui.QLabel):
    def __init__(self, parent=None):
        super(HoverLabel, self).__init__(parent)
        self.setMouseTracking(True)
##        self.setAcceptsHoverEvents(True)
##        self.oldpos = QtCore.QPoint(0, 0)

##    def hoverEnterEvent(self, event):
##        print "hoverEnterEvent"
##
##    def hoverLeaveEvent(self, event):
##        print "hoverLeaveEvent"

    def mouseMoveEvent(self, event):

        widgetPosition = self.mapFromGlobal(event.globalPos())
##        hovere= QtGui.QHoverEvent(QtCore.QEvent.HoverLeave,widgetPosition, self.oldpos )
##        self.oldpos  = widgetPosition
##        print widgetPosition

class MainWindow(QtGui.QMainWindow):
    def __init__(self,taglisting):
        super(MainWindow, self).__init__()

        widget = QtGui.QWidget()
        self.setCentralWidget(widget)

        self.taglisting = taglisting
        self.taglisting.subscribe(self)
        self.kaikkiKansionKuvatTagatty=False
        self.debug = False
        self.debugLog = ""
        self.debugLogFile = "debuglogi.txt"

        self.imgFileExtensionsRgx = r'\.(jpg)|(JPG)|(PNG)|(png)'
        handcursor= QtGui.QCursor(QtCore.Qt.OpenHandCursor)
##        self.setCursor(cursor)
        pyappfilepath = os.path.realpath(__file__)
##        print "pyappfilepath ",pyappfilepath
        self.appDirectory = os.path.dirname(pyappfilepath)
        print "appDirectory ", self.appDirectory

        self.temppubfolder="temp_publish_folder"
        self.autoNextPic=True
        self.listSubfolders=True
        self.kuvakansio=r"i:\kuvat"
        self.readPrefs()

        self.scanImagesFolder()

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
        self.debugLog += self.taglisting.debugLog
        self.jumpToUntagged()
        if self.debug:
            saveFile(self.appDirectory + "\\" + self.debugLogFile, self.debugLog)

        self.loadImg()

    def scanWithSubfolders(self):
        pass

    def scanImagesFolder(self):
        if self.listSubfolders:
            self.scanWithSubfolders()
        else:
            os.chdir(self.kuvakansio)
            tiedostotkansiossa= os.listdir(self.kuvakansio)

            kuvatiedostot=[self.kuvakansio +"\\" + tiedsto for tiedsto in tiedostotkansiossa if re.findall(self.imgFileExtensionsRgx, tiedsto[-5:]) !=[] ]
            self.kuvatiedostolista=kuvatiedostot
        self.volserial= getVolSerial()
        self.indx=0

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

        self.loadListByTagsAct = QtGui.QAction("Load imagelist By &Tag", self,
                shortcut=QtGui.QKeySequence("Ctrl+T"),
                statusTip="Load imagelist By Tag", triggered=self.loadImageListWithTag)



        self.loadPublishListAct = QtGui.QAction("&Load Publish List", self,
                shortcut=QtGui.QKeySequence("Ctrl+Alt+O"),
                statusTip="Load Publish List", triggered=self.loadPublishList)

        self.showPublishListAct = QtGui.QAction("&Show Publish List", self,
                shortcut=QtGui.QKeySequence("Ctrl+U"),
                statusTip="Show Publish List", triggered=self.showPublishList)

        self.savePubListAct   = QtGui.QAction("&Save Publish List", self,
                shortcut=QtGui.QKeySequence("Ctrl+Alt+S"),
                statusTip="Show Publish List", triggered=self.savePubList)

        self.copyPublishIMagesToTempFolderAct = QtGui.QAction("&Copy Images To Temp Folder", self,
                shortcut=QtGui.QKeySequence("Ctrl+Alt+C"),
                statusTip="Copy Images To Temp Folder", triggered=self.copyPublishIMagesToTempFolder)

        self.clearPubListAct = QtGui.QAction("&Clear Publish List", self,
                shortcut=QtGui.QKeySequence("Ctrl+Alt+R"),
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

##        self.boldAct = QtGui.QAction("&Bold", self, checkable=True,
##                shortcut="Ctrl+B", statusTip="Make the text bold",
##                triggered=self.bold)
##
##        boldFont = self.boldAct.font()
##        boldFont.setBold(True)
##        self.boldAct.setFont(boldFont)
##
##        self.italicAct = QtGui.QAction("&Italic", self, checkable=True,
##                shortcut="Ctrl+I", statusTip="Make the text italic",
##                triggered=self.italic)
##
##        italicFont = self.italicAct.font()
##        italicFont.setItalic(True)
##        self.italicAct.setFont(italicFont)
##
##        self.setLineSpacingAct = QtGui.QAction("Set &Line Spacing...", self,
##                statusTip="Change the gap between the lines of a paragraph",
##                triggered=self.setLineSpacing)
##
##        self.setParagraphSpacingAct = QtGui.QAction(
##                "Set &Paragraph Spacing...", self,
##                statusTip="Change the gap between paragraphs",
##                triggered=self.setParagraphSpacing)

        self.aboutAct = QtGui.QAction("&About", self,
                statusTip="Show the application's About box",
                triggered=self.about)

        self.aboutQtAct = QtGui.QAction("About &Qt", self,
                statusTip="Show the Qt library's About box",
                triggered=self.aboutQt)
        self.aboutQtAct.triggered.connect(QtGui.qApp.aboutQt)

##        self.leftAlignAct = QtGui.QAction("&Left Align", self, checkable=True,
##                shortcut="Ctrl+L", statusTip="Left align the selected text",
##                triggered=self.leftAlign)
##
##        self.rightAlignAct = QtGui.QAction("&Right Align", self,
##                checkable=True, shortcut="Ctrl+R",
##                statusTip="Right align the selected text",
##                triggered=self.rightAlign)
##
##        self.justifyAct = QtGui.QAction("&Justify", self, checkable=True,
##                shortcut="Ctrl+J", statusTip="Justify the selected text",
##                triggered=self.justify)
##
##        self.centerAct = QtGui.QAction("&Center", self, checkable=True,
##                shortcut="Ctrl+C", statusTip="Center the selected text",
##                triggered=self.center)

##        self.alignmentGroup = QtGui.QActionGroup(self)
##        self.alignmentGroup.addAction(self.leftAlignAct)
##        self.alignmentGroup.addAction(self.rightAlignAct)
##        self.alignmentGroup.addAction(self.justifyAct)
##        self.alignmentGroup.addAction(self.centerAct)
##        self.leftAlignAct.setChecked(True)


    def loadImageListWithTag(self):
        text, ok = QtGui.QInputDialog.getText(self, "Load imagelist with tag",
                "tag:", QtGui.QLineEdit.Normal,
                QtCore.QDir.home().dirName())
        if ok and text != '':
            print text
            self.kuvatiedostolista = []
            for kuva in self.taglisting.kuvatHash.keys():
                if text in self.taglisting.kuvatHash[kuva].decode("utf-8"):
##                    self.kuvatiedostolista
                    pass
##                    self.textLabel.setText(text)

    def createMenus(self):
        self.fileMenu = self.menuBar().addMenu("&File")
##        self.fileMenu.addAction(self.newAct)
        self.fileMenu.addAction(self.openAct)
##        self.fileMenu.addAction(self.saveAct)
        self.fileMenu.addAction(self.chooseFolderAct)

##        self.fileMenu.addAction(self.printAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAct)

##        self.editMenu = self.menuBar().addMenu("&Edit")
##        self.editMenu.addAction(self.undoAct)
##        self.editMenu.addAction(self.redoAct)
##        self.editMenu.addSeparator()
##        self.editMenu.addAction(self.cutAct)
##        self.editMenu.addAction(self.copyAct)
##        self.editMenu.addAction(self.pasteAct)
##        self.editMenu.addSeparator()

##        self.imagesMenu = self.menuBar().addMenu("&Images")
##        self.imagesMenu.addAction(self.jumpToIndexAct)
##        self.imagesMenu.addAction(self.loadListByTagsAct)

        self.publishMenu = self.menuBar().addMenu("&Publish")

##        self.publishMenu.addAction(self.loadPublishListAct)
##        self.publishMenu.addAction(self.showPublishListAct)
        self.publishMenu.addAction(self.savePubListAct)
        self.publishMenu.addAction(self.copyPublishIMagesToTempFolderAct)
        self.publishMenu.addAction(self.clearPubListAct)

##temp_publish_folder

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
                "Choose images folder",
                "popop", options)
        if directory:
##            self.directoryLabel.setText(directory)
            self.kuvakansio = directory
            self.scanImagesFolder()
            self.tagitlineEdit.setFocus()

            self.jumpToUntagged()
            print "self.indx " ,self.indx
            self.loadImg()
            self.tagitlineEdit.selectAll()

    def newFile(self):
        self.infoLabel.setText("Invoked <b>File|New</b>")

    def open(self):
        self.infoLabel.setText("Invoked <b>File|Open</b>")
        print self.appDirectory + "\\" + self.taglisting.luetteloTiedosto
        os.system(self.appDirectory + "\\" + self.taglisting.luetteloTiedosto)

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

    def loadPublishList(self):
        self.infoLabel.setText("Invoked <b>Load Publish List</b>")


    def showPublishList(self):
        self.infoLabel.setText("Invoked <b>Show Publish List</b>")
        print self.publishList

    def savePubList(self):
        self.infoLabel.setText("Invoked <b>Save Publish List</b>")
        list2save= self.kuvakansio + "\n" + "\n".join(self.publishList)
        tiednimi = self.appDirectory + "/publists/" + "publishlist_" + "{0:%d-%m-%Y-%H-%M-%S}".format(datetime.now()) + ".txt"
        saveFile(tiednimi, list2save)

    def copyPublishIMagesToTempFolder(self):
        self.infoLabel.setText("Invoked <b>Copy Publish IMages To Temp Folder</b>")
        for kuva in self.publishList:
            src = self.kuvakansio + "/" + kuva
            dest=self.appDirectory + "/" + self.temppubfolder +"/" + kuva
            print "copy: ", src , dest
            shutil.copy2( src , dest)

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
##
##    def bold(self):
##        self.infoLabel.setText("Invoked <b>Edit|Format|Bold</b>")
##
##    def italic(self):
##        self.infoLabel.setText("Invoked <b>Edit|Format|Italic</b>")
##
##    def leftAlign(self):
##        self.infoLabel.setText("Invoked <b>Edit|Format|Left Align</b>")
##
##    def rightAlign(self):
##        self.infoLabel.setText("Invoked <b>Edit|Format|Right Align</b>")
##
##    def justify(self):
##        self.infoLabel.setText("Invoked <b>Edit|Format|Justify</b>")
##
##    def center(self):
##        self.infoLabel.setText("Invoked <b>Edit|Format|Center</b>")
##
##    def setLineSpacing(self):
##        self.infoLabel.setText("Invoked <b>Edit|Format|Set Line Spacing</b>")
##
##    def setParagraphSpacing(self):
##        self.infoLabel.setText("Invoked <b>Edit|Format|Set Paragraph Spacing</b>")

    def about(self):
        self.infoLabel.setText("Invoked <b>Help|About</b>")
        QtGui.QMessageBox.about(self, "About Menu",
                "<b>Imagetagger</b> is a image tagging aplication."
                "Tag fast, find pics fast.")

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
        layout.setRowMinimumHeight(0, 300)
##        for i in range(Dialog.NumGridRows):

        vbox = QtGui.QVBoxLayout(self)

        dbutton = QtGui.QPushButton("&Delete"  )
        dbutton.setFocusPolicy(QtCore.Qt.NoFocus)
        vbox.addWidget(dbutton)
        unsharpbutton = QtGui.QPushButton("U&nsharp"  )
        unsharpbutton.setFocusPolicy(QtCore.Qt.NoFocus)
        vbox.addWidget(unsharpbutton)

        flkrbutton = QtGui.QPushButton("P&ublish"  )
        flkrbutton.setFocusPolicy(QtCore.Qt.NoFocus)
        vbox.addWidget(flkrbutton)

        lbutton = QtGui.QPushButton("P&revious"  )
        lbutton.setFocusPolicy(QtCore.Qt.NoFocus)
        vbox.addWidget(lbutton)
##        vbox.addSpacing(120)
        vbox.insertSpacing(1,20)

        layout.addLayout(vbox, 1, 0)
##        layout.addWidget(lbutton, 2, 0)

        rbutton = QtGui.QPushButton("Nex&t"  )
        rbutton.setFocusPolicy(QtCore.Qt.NoFocus)
        layout.addWidget(rbutton, 2, 5)


        dbutton.clicked.connect(self.markForDelete)
        unsharpbutton.clicked.connect(self.labelAsUnsharp)
        rbutton.clicked.connect(self.nextImage)

        lbutton.clicked.connect(self.prevImage)
        flkrbutton.clicked.connect(self.addToPublishList)


        tagitlabel = QtGui.QLabel("Search tags" )
        self.tagitlineEdit = QtGui.QLineEdit()

        self.tagitlineEdit.returnPressed.connect(self._lineedit_returnPressed)

        layout.addWidget(tagitlabel, 7, 0)
        layout.addWidget(self.tagitlineEdit, 7, 1)

        self.imageLabel = HoverLabel()
        self.imageLabel.setBackgroundRole(QtGui.QPalette.Base)
        self.imageLabel.setSizePolicy(QtGui.QSizePolicy.Ignored,QtGui.QSizePolicy.Ignored)

        frameStyle = QtGui.QFrame.Sunken | QtGui.QFrame.Panel
        #self.directoryLabel = QtGui.QLabel()
        #self.directoryLabel.setFrameStyle(frameStyle)
        #layout.addWidget(self.directoryLabel, 8, 1)

        titlelabel = QtGui.QLabel("Title" )
        self.titlelineEdit = QtGui.QLineEdit()
        layout.addWidget(titlelabel, 8, 0)
        layout.addWidget(self.titlelineEdit, 8, 1)
        self.titlelineEdit.returnPressed.connect(self._lineedit_returnPressed)

        ptagitlabel = QtGui.QLabel("Publish tags" )
        self.ptagitlineEdit = QtGui.QLineEdit()
        layout.addWidget(ptagitlabel, 9, 0)
        layout.addWidget(self.ptagitlineEdit, 9, 1)
        self.ptagitlineEdit.returnPressed.connect(self._lineedit_returnPressed)
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


##        wordList = ["alpha", "omega", "omicron", "zeta"]
        self.setCompleterList()

    def lasketagattyjenLukumaara(self):
        self.tagattyLukumaara=0
##        print self.taglisting.kuvatHash.keys()
        if self.debug:
            self.debugLog += "\nkuvatHash.keys()\n"
            self.debugLog += "\n".join(self.taglisting.kuvatHash.keys()).encode("utf-8") +"\n\n"
            self.debugLog += "kuvatiedostolista: \n"
        for i, kuva1 in enumerate( self.kuvatiedostolista):
##            print kuva
            kuva=os.path.basename(kuva1)
            if self.debug:
                self.debugLog += kuva + "\n"
            if kuva in self.taglisting.kuvatHash.keys():
                self.tagattyLukumaara +=1

    def jumpToUntagged(self):
        self.lasketagattyjenLukumaara()
        if self.tagattyLukumaara < len(self.kuvatiedostolista):
            for i, kuva1 in enumerate( self.kuvatiedostolista):
                kuva=os.path.basename(kuva1)
                if kuva not in self.taglisting.kuvatHash.keys():
                    break
            self.indx=i
        else:
            self.kaikkiKansionKuvatTagatty = True
            self.indx=0

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
        koko = str(os.stat(tiedosto).st_size)#  / 1000 ) + "kb"
        koko
        timenowstr= "{0:%d.%m.%Y %H:%M:%S}".format(datetime.now())
        tagirivi = self.kuvatiedostolista[self.indx]+" | "+ self.tagitlineEdit.text() +" | "+ date_taken + " " + time+" "+self.pixkoko+" "+koko+" | "
        tagirivi += self.kuvakansio +" | tagd: " + timenowstr + " | volserial: " + self.volserial
        tagirivi += " | title: " + self.titlelineEdit.text()  + " | pubtags: " + self.ptagitlineEdit.text() +"\n"
        print tagirivi
        self.taglisting.lisaaTagi(self.tagitlineEdit.text(), tagirivi)
        self.lastTagi=self.tagitlineEdit.text()
        self.setCompleterList()
        self.tagitlineEdit.setText( self.lastTagi.replace(",UNSHARP","").replace(",DELETE",""))
        self.titlelineEdit.setText("")
        self.ptagitlineEdit.setText("")

        if self.autoNextPic:
            self.nextImage()


    def setImageInfoLabel(self):
        fileName = self.kuvatiedostolista[self.indx]
        infotxt = "Kansio: " + self.kuvakansio + "     kuva: " +fileName
        infotxt += "    " + str(self.indx+1) +"/" + str( len(self.kuvatiedostolista))
        infotxt += "    otettu: " +  get_date_taken(fileName)
        if self.kaikkiKansionKuvatTagatty:
            infotxt += "   Kaikki kansion " +str(self.tagattyLukumaara) + " kuvaa jo tagatty"
        else:
            infotxt += "    tagatty: " +  str(self.tagattyLukumaara) +"/" + str( len(self.kuvatiedostolista))
        self.infolabel.setText(infotxt)

    def loadImg(self):
        fileName = self.kuvatiedostolista[self.indx] #r"E:\kuvat\IMG_2561.JPG"
        self.setImageInfoLabel()
##        self.infolabel.setText(infotxt)
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
        kuva=os.path.basename(self.kuvatiedostolista[self.indx])
        if unicode( kuva) in self.taglisting.kuvatHash.keys() :  #jos kuva on jo luettelossa
            try:
                self.tagitlineEdit.setText( self.taglisting.kuvatHash[kuva].decode("utf-8"))
            except:
                self.tagitlineEdit.setText( self.taglisting.kuvatHash[kuva])
##        else:
##            self.tagitlineEdit.setText("")
        self.imageLabel.setPixmap(pxmap)

##        self.scaleFactor = 0.5

    def appendToTags(self,tagtxt):
##        self.tagitlineEdit.text()
        self.tagitlineEdit.setText(  self.tagitlineEdit.text() +"," + tagtxt)

    def markForDelete(self):
        self.appendToTags("DELETE")

    def labelAsUnsharp(self):
        self.appendToTags("UNSHARP")

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
    ohjelmapath=os.path.dirname(os.path.realpath(__file__))
    print "ohjelmapath ", ohjelmapath
    tagilistMangr= TagListingManager(ohjelmapath)
##    dialog = Dialog(tagilistMangr)
    window = MainWindow(tagilistMangr)
    desktoppi= app.desktop()
    screengeom= desktoppi.screenGeometry()
    print "screenGeometry w ", screengeom.width()
    screenWidth = screengeom.width()
    screenHeight = screengeom.height()
    window.show()
    width= window.height()
    height = window.width()
##    print (screenWidth/2)-(width/2),(screenHeight/2)-(height/2),width,height
    window.setGeometry(40,30, 900, 700)
##    window.setGeometry((screenWidth/2)-(width/2),(screenHeight/2)-(height/2),width,height)


    sys.exit(app.exec_())
