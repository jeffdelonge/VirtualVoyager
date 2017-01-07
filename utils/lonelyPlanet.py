from bs4 import BeautifulSoup
import urllib2
import requests
from selenium import webdriver
from pyvirtualdisplay import Display
import requests
import sys

def main():
    f = open('out.txt', 'w')

    keyword = "rock climbing"#" ".join(sys.argv[1:])
    destinations = get_best_locations(keyword)#get_best_location(keyword)
    for destination,image in destinations:
        print destination, image

def get_best_locations(keyword): 
    destinations = []

    keyword = urllib2.quote(keyword)
    url = "http://www.lonelyplanet.com/search?q="+keyword+"&type=place"

    #website prevents bot scraping. pretend to be mozilla
        #request = urllib2.Request(url, headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0"})
        #webpage = urllib2.urlopen(request).read()
    request = requests.get(url, headers = {"User-Agent": "Mozilla/5.0 (XLL; Linux x86_64; rv:45.0) Gecko/20100101 Thunderbird/45.4.0"})
    webpage = request.text
    soup=BeautifulSoup(webpage, "lxml")
    #print soup.prettify().encode('UTF-8')

    content = soup.find_all("a", class_="link--wrapper")
    for i in [0,2,3,4,5]:
        result = content[i]
        name = result.find_all("h3", class_="search__result-title copy--h1")[0]
        destination = name.getText().strip()#' '.join(topResult.getText().strip().split()[1:])
        smallImage = result.find('img')['src']
        image = smallImage[smallImage.index('http'):]
        destinations.append((destination, image))


    return destinations

def selenium(keyword):
	destinations = []
	keyword = urllib2.quote(keyword)
	url = 'http://www.lonelyplanet.com/search?q={}&type=place'.format(keyword)
	print(requests.get(url).status_code)
	display = Display(visible=0, size=(800,600))
	display.start()
	driver = webdriver.Firefox()#executable_path='../../../../bin/geckodriver'); print 'hello'
	driver.get(url)
	webpage = driver.page_source
	driver.close()
	
	soup=BeautifulSoup(webpage, "lxml")
    #print soup.prettify().encode('UTF-8')

	content = soup.find_all("a", class_="link--wrapper")
	for i in [0,2,3,4,5]:
		result = content[i]
		name = result.find_all("h3", class_="search__result-title copy--h1")[0]
		destination = name.getText().strip()
		smallImage = result.find('img')
		if smallImage:
		    smallImage = smallImage['src']
		    image = smallImage[smallImage.index('http'):]
		else:
		    image = None
		destinations.append((destination, image))

	return destinations

if __name__ == "__main__":
    main()

