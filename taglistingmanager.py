
from datetime import datetime



def lataaTiedosto(lataatama):

    try:
        f = open(lataatama, 'r')
    except:
        tnimi = lataatama
        now = datetime.now()
        sisalto = self.luontikaneetti+str( now) +"\n"
        sisalto += self.sarakkeidenselitys +"\n"
        saveAFile(tnimi, sisalto)

        f = open(lataatama, 'r')
    loadedFileContent=f.read()
    f.close()
    return loadedFileContent

def saveAFile(filename,content):
    f = open(filename, 'w')
    f.write(content)
    f.close()

def tallennaTied(tiednimi,sisalto):
    print "tallennus"
    f = open(tiednimi, 'a')
    f.write(sisalto.encode("utf-8"))
    f.close()


class TagListingManager(object):


    def __init__(self,ohjelmapath):
##        ohjelmapath=r"E:\python\imagetagger"
##        self.state = gui
        self.ohjelmapath=ohjelmapath
        self.kuvatHash = {}
        self.luetteloTiedosto = "tagiluettelo.txt"

        self.luontikaneetti = "uusi tagi lista luotu: "
        self.sarakkeidenselitys = "tiedostonimi | tagit | kuvatiedoston last modified kuvapixelikoko kuvatiedosto koko | sijaintikansio | tagirivin luontihetki"
        self.state = None

        kuvalistaus = lataaTiedosto(self.ohjelmapath+"/"+self.luetteloTiedosto)
        kuvalistaus[:200]
        kuvalistausArr = kuvalistaus.split("\n")
        print "kuvalistausArr[0] ",kuvalistausArr[0]
        if self.luontikaneetti[0:9] in kuvalistausArr[0]:
            kuvalistausArr.pop(0)
            print "kuvalistausArr[0] ",kuvalistausArr[0]

        selitysrivinalku = "tiedostonimi | tagit | kuvatiedoston last modified kuvapixelikoko"
        if selitysrivinalku in kuvalistausArr[0]:
            kuvalistausArr.pop(0)
            print "kuvalistausArr[0] ",kuvalistausArr[0]


	for i in range(len(kuvalistausArr)):
		tagriviarray=kuvalistausArr[i].split("|")
		#puts tagriviarray.size
        if len(tagriviarray) >= 3 and len( tagriviarray) <= 5:
            self.kuvatHash[tagriviarray[0].strip()]=tagriviarray[1].strip()
##    self.kuvatHash.keys()[:5]

##
    def subscribe(self,state):
        self.state = state


    def lisaaTagi(self,tagi, tagirivi):
        if self.state.kuvatiedostolista[self.state.indx] not in  self.kuvatHash.keys():
            self.kuvatHash[self.state.kuvatiedostolista[self.state.indx]]  = tagi
            tallennaTied(self.ohjelmapath+"/"+self.luetteloTiedosto, tagirivi)
        elif tagi != self.kuvatHash[self.state.kuvatiedostolista[self.state.indx]]:
            tallennaTied(self.ohjelmapath+"/"+self.luetteloTiedosto, tagirivi)
        else:
            print "identtinen on jo"



