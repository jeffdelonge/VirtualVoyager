from __init__ import app, conn, cur
from pprint import pprint
import json
from views import get_location_coords

def grabText(startHeader, endHeader, text):
	startIndex = text.find(startHeader)
	if (startIndex == -1):
		print "ERROR: startHeader not found"
		return "EMPTY"

	startIndex += len(startHeader)
	resultText = text[startIndex:]
	endIndex = resultText.find(endHeader)
	if (endIndex == -1):
		print "ERROR: endHeader not found"
		return "EMPTY"

	resultText = resultText[:endIndex]
	return resultText


def grabGoNexts(text):
	startIndex = text.find('==Go next==\n')
	if (startIndex == -1):
		print "Go next header not found"
		return ["EMPTY"]

	goNextText = text[startIndex:]
	stopIndex = goNextText.find('{{')
	if (goNextText.find('[[') > stopIndex):
		print "No Go Nexts found"
		return ["EMPTY"]

	goNexts = []
	place = grabText('[[', ']]', goNextText)
	if (place == "EMPTY"):
		print "No Go Nexts found"
		return ["EMPTY"]
	if ('|' in place):
		place = place[:place.find('|')]
	position = goNextText.find(']]')
	goNextText = goNextText[position+2:]
	i = 0
	while place != "EMPTY":
		place = place.replace(' ', '_').encode('utf-8')
		if (place not in goNexts):
			goNexts.append(place)
		print place
		stopIndex = goNextText.find('{{')
		if (goNextText.find('[[') > stopIndex):
			print "No more Go Nexts found"
			break
		place = grabText('[[', ']]', goNextText)
		if (place == "EMPTY"):
			break
		if ('|' in place):
			place = place[:place.find('|')]	
		position = goNextText.find(']]')
		goNextText = goNextText[position+2:]

	return goNexts

#cur.execute('INSERT INTO Location (Name) VALUES (\"{}\")'.format("TEST INSERT FROM PYTHON"))
with open('pages.json') as data_file:
	data = json.load(data_file)

for page in data['pages']:
#	if page['page_title'] != 'Chicago':
#		continue
	print ""
	print page['page_title']
	searchName = page['page_title'].replace("_", " ")
#	xycoords = get_location_coords(searchName)
#	xcoord = xycoords[0]
#	ycoord = xycoords[1]
#	print "{}, {}".format(xcoord,ycoord)
	text = page['old_text']
	text = text.replace("\"", "")
	text = text.replace("\'", "")
#	print text
	name = page['page_title'].encode('utf-8')
	goNexts = grabGoNexts(text)
	print goNexts
#	for loc in goNexts:
#		cur.execute('INSERT INTO `Location Go Next` (SourceName, NextName) VALUES (\"{}\",\"{}\")'.format(name, loc))

#	see = grabText('==See==\n', '\n==', text).encode('utf-8')
#	eat = grabText('==Eat==\n', '\n==', text).encode('utf-8')
#	do  = grabText('==Do==\n',  '\n==', text).encode('utf-8')
#	description = grabText('==Understand==\n', '\n==', text).encode('utf-8')

#	cur.execute('INSERT INTO Location (Coordinates, Description, Do, Eat, Name, See) VALUES (0,\"{}\",\"{}\",\"{}\",\"{}\",\"{}\")'.format(description, do, eat, name, see))

#conn.commit()

