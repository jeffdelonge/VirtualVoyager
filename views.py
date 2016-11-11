from __init__ import app, cur 
from flask import render_template
import requests

#lonely planet imports
from bs4 import BeautifulSoup
import urllib2

@app.route('/')
def welcome():
    return render_template('index.html') 


@app.route('/example_query')
def example_query():
    cur.execute("SELECT page_title FROM page WHERE page_title LIKE '%Republic%'")
    query_name = "SELECT page_title FROM page WHERE page_title LIKE '%Republic%'" 
    query = str(cur.fetchall())
    return render_template('example_query.html', query_name=query_name, query=query) 


@app.route('/virtualvoyager/trips/<keyword>', methods=['GET'])
def get_trip(keyword):
    return "hello"


def get_best_location(keyword):
    '''
    Make requests to LostVoyager API with the user inputted keyword
    Choose most popular location from request
    Return information needed to make trip and location AND IMAGE URL
    '''


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


def get_location_coords(location_name):
    rv = requests.get('http://maps.googleapis.com/maps/api/geocode/json?address={}&key=AIzaSyCoIJcakxVen5qGdu_PsV_ajdl33qwGskI'.format(location_name))
    data = rv.json()
    coords = data['results']['geometry']['location']
    return (coords['lat'], coords['lng'])


def get_location_data(location_name, location_coords):
    '''
    Get dictionary of data associated with location 
    '''
    
    # Get the page associated with the location
    cur.execute("SELECT page_id FROM page WHERE page_title={}".format(location))
    page_id = cur.fetchone()

    # Get the wiki text associated with the page
    cur.execute("SELECT old_text FROM text WHERE old_id={}".format(page_id))
    location_text = cur.fetchone()

    # Process text and return dict 
    location_dict = process_wiki_text(location_text)
    if location_coords:
        location_dict['coords'] = location_coords
    else:
        location_dict['coords'] = get_location_coords(location_name)
    return location_dict
    

def process_wiki_text(text):
    '''
    Extract pictures, description, eat, see, do, and go next from wiki text
    '''
    return 'hello'


def create_location(location_name, location_coords=None):
    '''
    Create location 
    '''
    return 'hello'


def get_location_by_name(name):
    cur.execute("SELECT * FROM Location WHERE name={}".format(name))
    location = cur.fetchone()
    return location


def get_location_by_coords(coords):
    cur.execute("SELECT * FROM Location WHERE Coordinates={}".format(coords))
    location = cur.fetchone()
    return location


def create_trip_location(keyword, coords, name):
    cur.execute('INSERT INTO TripLocation VALUES ({},{})'.format(keyword, coords, name))


def create_trip(keyword, location_coordinates, user, date):
    '''
    Create trip from location's go next 
    '''

    # Get all associated go nexts with location
    cur.execute('''
                SELECT next_name, next_coords 
                FROM Location Go Next 
                WHERE source_coords={}
                '''.format(location_coordinates))
    rv = cur.fetchall()
    if not rv:
        raise ValueError('Location with coordinates {} does not exist'.format(location_coordinates))

    # Get info and create location for all go nexts
    locations = []
    for location in rv:
        new_location = get_location_by_coords(location[1])
        if not location:
            create_location(location[0], location[1])
        create_trip_location(keyword, location[1], location[0])
    
    cur.execute('''
                INSERT INTO Trip
                VALUES ({}, {}, {})
                '''.format(user, keyword, date))
     
    

