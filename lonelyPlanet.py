from bs4 import BeautifulSoup
import urllib2

def main():
    keyword = "taj mahal"
    destination, image = get_best_location(keyword)
    print destination
    print image

def get_best_location(keyword):
    keyword = urllib2.quote(keyword)
    url = "http://www.lonelyplanet.com/search?q="+keyword+"&type=place"

    #website prevents bot scraping. pretend to be mozilla
    request_headers = {
        "Accept-Language": "en-US,en;q=0.5",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": url,
        "Connection": "keep-alive"
    }

    request = urllib2.Request(url, headers = request_headers)
    webpage = urllib2.urlopen(request).read()
    soup=BeautifulSoup(webpage, "lxml")
    #print soup.prettify().encode('UTF-8')

    content = soup.find_all("a", class_="link--wrapper")
    topResult = content[0]
    destination = ' '.join(topResult.getText().strip().split()[1:])
    smallImage = topResult.find('img')['src']
    image = smallImage[smallImage.index('http'):]

    return destination, image


if __name__ == "__main__":
    main()

