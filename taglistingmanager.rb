

class TagListingManager

attr_reader :kuvatHash
attr_writer :kuvatHash

def lataaTiedosto(lataatama)

begin 
f = File.open(lataatama)
rescue Exception => e 
tnimi = lataatama
now = Time.now
sisalto = @luontikaneetti+now.to_s+"\n"
sisalto += @sarakkeidenselitys +"\n"
tallennaTied(tnimi, sisalto)
end
f = File.open(lataatama)
tiedstr= f.read
f.close
tiedstr
end

def tallennaTied(tnimi, sisalto)
puts "tallennus"
aFile = File.new(tnimi, "a")
aFile.write(sisalto)
aFile.close
end

def initialize

@kuvatHash = {}
@luetteloTiedosto = "tagiluettelo.txt"

@luontikaneetti = "uusi tagi lista luotu: "
@sarakkeidenselitys = "tiedostonimi | tagit | kuvatiedoston last modified kuvapixelikoko kuvatiedosto koko | sijaintikansio | tagirivin luontihetki"
@state = nil

kuvalistaus = lataaTiedosto($ohjelmapath+"/"+@luetteloTiedosto)
kuvalistausArr = kuvalistaus.split("\n")
print "kuvalistausArr[0] ",kuvalistausArr[0]; puts
if kuvalistausArr[0].include?(@luontikaneetti[0,9])
kuvalistausArr.shift
print "kuvalistausArr[0] ",kuvalistausArr[0]; puts
end
selitysrivinalku = "tiedostonimi | tagit | kuvatiedoston last modified kuvapixelikoko"
if kuvalistausArr[0].include?(selitysrivinalku)
kuvalistausArr.shift
print "kuvalistausArr[0] ",kuvalistausArr[0]; puts
end

	for i in 0..kuvalistausArr.size-1
		tagriviarray=kuvalistausArr[i].split("|")
		#puts tagriviarray.size
		if tagriviarray.size >= 3 and tagriviarray.size <= 5
		@kuvatHash[tagriviarray[0].strip]=tagriviarray[1].strip
		end
	end

end

def subscribe(state)
@state = state
end

def lisaaTagi(tagi, tagirivi)
if  @kuvatHash[@state.kuvatiedostolista[@state.indx]] == nil
@kuvatHash[@state.kuvatiedostolista[@state.indx]]  = tagi
tallennaTied($ohjelmapath+"/"+@luetteloTiedosto, tagirivi)
elsif tagi != @kuvatHash[@state.kuvatiedostolista[@state.indx]]
tallennaTied($ohjelmapath+"/"+@luetteloTiedosto, tagirivi)
else
puts "identtinen on jo"
end

end
end