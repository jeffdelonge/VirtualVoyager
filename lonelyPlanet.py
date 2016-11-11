from bs4 import BeautifulSoup
import urllib2
import requests

def main():
    keyword = "rock climbing"
    destinations = get_best_location(keyword)
    for destination,image in destinations:
        print destination, image

def get_best_location(keyword):
    destinations = []

    keyword = urllib2.quote(keyword)
    url = "http://www.lonelyplanet.com/search?q="+keyword+"&type=place"

    #website prevents bot scraping. pretend to be mozilla
        #request = urllib2.Request(url, headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0"})
        #webpage = urllib2.urlopen(request).read()
    request = requests.get(url, headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0"})
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


if __name__ == "__main__":
    main()

