import json
from pprint import pprint

def parseFor(text, startHeader, endHeader):
	startIndex = text.find(startHeader)
        newText = text[startIndex:]
	endIndex = newText.find(endHeader)
	if (startIndex == -1 or endIndex == -1):
		print "start or end header not found!"
		return

	resultString = text[startIndex+8:endIndex-1]
	return resultString

#medium_test is 60000 words or more per page
with open('finalpages.json') as data_file:
	data = json.load(data_file)

for page in data['pages']:
	print page['page_title']
	text = page['old_text']
#	print "SEE"
#	print parseFor(text, '==See==', '\n==Do==')
#	print "DO"
#	print parseFor(text, '==Do==', '\n==Buy==')
#	print "EAT"
#	print parseFor(text, '==Eat==', '\n==Drink==')
        print parseFor(text, '==Understand==', '\n==')
