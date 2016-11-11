from __init__ import app, conn, cur
from pprint import pprint
import json

def grabText(startHeader, endHeader, text):
	startIndex = text.find(startHeader) + len(startHeader)
	if (startIndex == -1):
		print "ERROR: startHeader not found"
		return "EMPTY"

	resultText = text[startIndex:]

	endIndex = resultText.find(endHeader)
	if (endIndex == -1):
		print "ERROR: endHeader not found"
		return "EMPTY"

	resultText = resultText[:endIndex]
	return resultText

#cur.execute('INSERT INTO Location (Name) VALUES (\"{}\")'.format("TEST INSERT FROM PYTHON"))

with open('pages.json') as data_file:
	data = json.load(data_file)

for page in data['pages']:
	print page['page_title']
	text = page['old_text']
	text = text.replace("\"", "")
	text = text.replace("\'", "")
	name = page['page_title'].encode('utf-8')
	see = grabText('==See==\n', '\n==', text).encode('utf-8')
	eat = grabText('==Eat==\n', '\n==', text).encode('utf-8')
	do  = grabText('==Do==\n',  '\n==', text).encode('utf-8')
	description = grabText('==Understand==\n', '\n==', text).encode('utf-8')
	goNext = grabText('==Go Next==\n', '\n==', text).encode('utf-8')

	cur.execute('INSERT INTO Location (Coordinates, Description, Do, Eat, Name, See) VALUES (0,\"{}\",\"{}\",\"{}\",\"{}\",\"{}\")'.format(description, do, eat, name, see))

conn.commit()
