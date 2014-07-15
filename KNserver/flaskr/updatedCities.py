import urllib2

def getCitiesHTML():
	url = "http://baixing.com/?changeLocation=yes"    
	html = urllib2.urlopen(url)    
	myFile = open("Baixing_citySourceCode.txt", "w")
	for line in html:
		myFile.write(line)
	myFile.close
	
def parseCities():
	citiesDict = {}  #pinyin : char
	content = ""
	myFile = open("Baixing_citySourceCode.txt", "r")
	for line in myFile:
		content += line
	
	start = content.find("new_cities")
	end = content.find("</tr></table></table>")
	citiesPortion = content[start : end]
	pinStart = citiesPortion.find("://") + 3
	firstCityPortion = citiesPortion[pinStart: ] #reduces each iteration of below "for" loop
	
	pinCity = ""
	charCity = ""
	newCycleStart = 0
	
	for c in firstCityPortion :
		if c != "." :
			pinCity += c
		else : 
			pinCityEnd = firstCityPortion.find(c) #c=".", index relative to start of pin city name
			charStart = pinCityEnd + 15
			for z in firstCityPortion[15: ] :
				if z != "<" :
					charCity += z
				else :
					charCityEnd = firstCityPortion.find(z) #z="<", index relative to start pin city name
					newCycleStart = charCityEnd + 20
					break
			
			citiesDict[pinCity] = charCity
			pinCity = ""
			charCity = ""
			
			try: 
				firstCityPortion = firstCityPortion[charCityEnd + 20]  #can you change what you're "for"-ing over from within the for loop?
																#this is where you reduce (start later) firstCityPortion
			except IndexError:  #only happens once all cities exhausted
				break
					
	parsedCitiesFile = open("Parsed_Cities.txt", "w")
	parsedCitiesFile.write(str(citiesDict))
	parsedCitiesFile.close()
	


	
