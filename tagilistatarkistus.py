

import re
from PySide import  QtGui
from datetime import datetime

def lataaTied(tiednimi):
    f = open(tiednimi, 'r')
    html_doc=f.read()
    f.close()
    return html_doc

def tallennaTied(tiednimi,sisalto):
    print "tallennus"
    f = open(tiednimi, 'a')
    f.write(sisalto.encode("utf-8"))
    f.close()


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

self_ohjelmapath=r"E:\python\imagetagger"
self_kuvatHash = {}
self_luetteloTiedosto = "tagiluettelo.txt"

self_luontikaneetti = "uusi tagi lista luotu: "
self_sarakkeidenselitys = "tiedostonimi | tagit | kuvatiedoston last modified kuvapixelikoko kuvatiedosto koko | sijaintikansio | tagirivin luontihetki"
self_state = None
self_debugLog = ""
kuvalistaus = lataaTied(self_ohjelmapath+"/"+self_luetteloTiedosto)
kuvalistaus[:200]
kuvalistausArr = kuvalistaus.split("\n")
print "kuvalistausArr[0] ",kuvalistausArr[0]
if self_luontikaneetti[0:9] in kuvalistausArr[0]:
    kuvalistausArr.pop(0)
    print "kuvalistausArr[0] ",kuvalistausArr[0]

selitysrivinalku = "tiedostonimi | tagit | kuvatiedoston last modified kuvapixelikoko"
if selitysrivinalku in kuvalistausArr[0]:
    kuvalistausArr.pop(0)
    print "kuvalistausArr[0] ",kuvalistausArr[0]
print "len(kuvalistausArr) ",len(kuvalistausArr)
i = 2000

kuvainfoObjs=[]

self_kuvatHash={}
dupsii=[]
for i in range(len(kuvalistausArr)):
    tagriviarray=kuvalistausArr[i].split("|")
    #puts tagriviarray.size
    tagriviarray
    infohash={}
    if len(tagriviarray) >= 3 :#and len( tagriviarray) <= 5:
        infohash['filename']=tagriviarray[0].strip()
        infohash['tags']=tagriviarray[1].strip()
        if "UNSHARP" in infohash['tags']:
            infohash['unsharp']= True
        if "DELETE" in infohash['tags']:
            infohash['pendingdelete']= True

        etadataar= tagriviarray[2].strip().split()
        etadataar
        infohash['metadatalistlen']= len(etadataar)
        infohash['metadata']= etadataar
        if infohash['metadatalistlen'] > 4:
            infohash['pictaken']= " ".join( etadataar[:2])
            infohash['lastmodified']= " ".join( etadataar[2:4])
            infohash['pixsize']=  etadataar[4]
            infohash['size']=  etadataar[5]
        elif infohash['metadatalistlen'] == 4:
            infohash['lastmodified']= " ".join( etadataar[:2])
            infohash['pixsize']=  etadataar[2]
            infohash['size']=  etadataar[3]
        else:
            infohash['lastmodified']= etadataar[0]
            infohash['pixsize']=  etadataar[1]
            infohash['size']=  etadataar[2]
        if len(tagriviarray) > 3:
            infohash['folderpath']=tagriviarray[3].strip()
            infohash['fullpath'] = infohash['folderpath'] + "\\" +infohash['filename']
        if len(tagriviarray) > 4:
##        tagriviarray[4]
            tagriviarray
            infohash['taggedtime']=re.findall(r'tagg?e?d:\s+(.*?)$',tagriviarray[4])[0].strip()
        if len(tagriviarray) > 5:
            infohash['volserial']=re.findall(r':\s+([A-Z0-9]+\-[A-Z0-9]+)\s*$',tagriviarray[5])[0].strip()
        if len(tagriviarray) > 6:
            infohash['title']=re.findall(r'title:\s+(.*?)$',tagriviarray[6])[0].strip()
        if len(tagriviarray) > 7:
            infohash['pubtags']=re.findall(r'pubtags:\s+(.*?)$',tagriviarray[7])[0].strip()

        infohash



        kuvakey=unicode( infohash['filename'].decode("utf-8"))
        kuvainfo = ImageInfo(kuvakey, 'tagilista')
        kuvainfo.filename  = infohash['filename']
        try:
            kuvainfo.fullpath  = infohash['fullpath']
            kuvainfo.folderpath  = infohash['folderpath']
        except:
            pass
        try:
            kuvainfo.size  = infohash['size']
        except:
            pass
        try:
            kuvainfo.lastmodified = infohash['lastmodified']
        except:
            pass
        try:
            kuvainfo.pictaken = infohash['pictaken']
        except:
            pass
        try:
            kuvainfo.tags = infohash['tags']
        except:
            pass
        try:
            kuvainfo.title = infohash['title']
        except:
            pass
        try:
            kuvainfo.pubtags = infohash['pubtags']
        except:
            pass
        try:
            kuvainfo.pixsize = infohash['pixsize']
        except:
            pass
        try:
            kuvainfo.volserial  = infohash['volserial']
        except:
            pass
        try:
            kuvainfo.taggedtime  = infohash['taggedtime']
        except:
            pass
        try:
            kuvainfo.unsharp  = infohash['unsharp']
        except:
            pass
        try:
            kuvainfo.pendingdelete  = infohash['pendingdelete']
        except:
            pass

        kuvainfoObjs.append(kuvainfo)
        if kuvakey not in self_kuvatHash.keys():
            self_kuvatHash[kuvakey]=infohash
            self_debugLog += tagriviarray[0].strip() +": " + tagriviarray[1].strip() + "\n"
        elif 'folderpath' in self_kuvatHash[kuvakey].keys() and 'folderpath' in infohash.keys() and self_kuvatHash[kuvakey]['folderpath'] == infohash['folderpath']:
            self_kuvatHash[kuvakey]=infohash
        elif 'metadata' in self_kuvatHash[kuvakey].keys() and 'metadata' in infohash.keys() and self_kuvatHash[kuvakey]['metadata'] == infohash['metadata']:
            self_kuvatHash[kuvakey]=infohash
        else:
            dupsii.append((self_kuvatHash[kuvakey],infohash))

len(dupsii)
dupsii
dupsii[0][0]
dupsii[0]
dupsii[1]
dupsii[2]
dupsii[0][0]['filename']
dupsii[0][1]['filename']
dupsii[0][0]['metadata']
dupsii[0][1]['metadata']
len( self_kuvatHash.keys())

len(kuvainfoObjs)
kuvainfoObjs[-1].filename
kuvainfoObjs[-1].fullpath
kuvainfoObjs[-1].folderpath
kuvainfoObjs[-1].size
kuvainfoObjs[-1].lastmodified
kuvainfoObjs[-1].pictaken
kuvainfoObjs[-1].tags
kuvainfoObjs[-1].title
kuvainfoObjs[-1].pubtags
kuvainfoObjs[-1].pixsize
kuvainfoObjs[-1].volserial
kuvainfoObjs[-1].taggedtime
kuvainfoObjs[-1].unsharp
kuvainfoObjs[-1].pendingdelete
kuvainfoObjs[-1].infosource


kuvainfoObjs[-1].lastmodified
kuvainfoObjs[-1].pictaken
kuvainfoObjs[-1].taggedtime

datetime.strftime(kuvainfoObjs[-1].taggedtime)

self_kuvatHash.keys()[:7]
self_kuvatHash.values()[:7]

len(kuvalistausArr)

infohkeys= self_kuvatHash[self_kuvatHash.keys()[-1]].keys()
infohkeys
infokeysvalueshash={}
for key in infohkeys:
    infokeysvalueshash[key]=[]

for key in  self_kuvatHash.keys():
    key
    for infokey in infohkeys:
        if infokey in self_kuvatHash[key].keys():
            infokeysvalueshash[infokey].append( self_kuvatHash[key][infokey])

infokeysvalueshash.keys()
len( infokeysvalueshash.keys())

infokeysvalueshash[infokeysvalueshash.keys()[0]][:9]
key=infokeysvalueshash.keys()[10]
key
valuelist= infokeysvalueshash[key]
len(valuelist)
valuelist[:9]
set( valuelist)
len( set( valuelist))
len( [valitem for valitem in valuelist if re.findall(r'\d+X\d+',valitem)!=[]])
len( [valitem for valitem in valuelist if re.findall(r'\d+(?:kb)?',valitem)!=[]])
len( [valitem for valitem in valuelist if re.findall(r'(DSC)|(IMG_)',valitem)!=[]])
[valitem for valitem in valuelist if re.findall(r'(DSC)|(IMG_)',valitem)==[]]
len( [valitem for valitem in valuelist if re.findall(r'[A-Z0-9]+\-[A-Z0-9]+',valitem)!=[]])
len( [valitem for valitem in valuelist if re.findall(r'\d+[\-\.]\d+[\-\.]\d+\s+\d+:\d+:\d+',valitem)!=[]])
len( [valitem for valitem in valuelist if re.findall(r'\d+[\-\.:]\d+[\-\.:]\d+\s+\d+:\d+:\d+',valitem)!=[]])
len( [valitem for valitem in valuelist if re.findall(r'\d+[\-\.]\d+[\-\.]\d+(?:\s+\d+:\d+:\d+)?',valitem)!=[]])