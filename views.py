from __init__ import app, cur 
from flask import render_template
import requests
import datetime

#lonely planet imports
from bs4 import BeautifulSoup
import urllib2

@app.route('/')
def welcome():
    return render_template('webpage/index.html') 


@app.route('/example_query')
def example_query():
    cur.execute("SELECT page_title FROM page WHERE page_title LIKE '%Republic%'")
    query_name = "SELECT page_title FROM page WHERE page_title LIKE '%Republic%'" 
    query = str(cur.fetchall())
    return render_template('example_query.html', query_name=query_name, query=query) 


@app.route('/trips/<keyword>', methods=['GET'])
def get_trip(keyword):
    '''cur.execute("SELECT * FROM Trip WHERE Keyword='{}'".format(keyword))
    trip = cur.fetchone()
    if trip:
        keyword = trip[1]
        cur.execute(
                    SELECT l1.Coordinates, l1.Description, l1.Eat, l1.See, l1.Do, l1.Name
                    FROM Location l1, TripLocation tl1
                    WHERE tl1.Trip={} AND l1.name = tl1.location_name
                    .format(keyword))
        trip = [location_to_dict(location) for location in cur.fetchall()]'''
    #else:
    locations = get_best_location(keyword);
    
    return render_template('webpage/trip.html', trip=trip)


def get_best_location(keyword):
    '''
    Make requests to LostVoyager API with the user inputted keyword
    Choose most popular locations from request
    Return information needed to make trip and location AND IMAGE URL
    '''

    destinations = []

    keyword = urllib2.quote(keyword)
    url = "http://www.lonelyplanet.com/search?q="+keyword+"&type=place"

    #website prevents bot scraping. pretend to be mozilla
    request_headers = {
        "Accept-Language": "en-US,en;q=0.5",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": url
    }

    request = urllib2.Request(url, headers = request_headers)
    webpage = urllib2.urlopen(request).read()
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


def get_location_by_name(name):
    cur.execute('SELECT * FROM Location WHERE name="{}"'.format(name))
    location = cur.fetchone()
    return location


def get_location_by_coords(coords):
    cur.execute('SELECT * FROM Location WHERE Coordinates={}'.format(coords))
    location = cur.fetchone()
    return location


def create_trip_location(keyword, coords, name):
    cur.execute('INSERT INTO TripLocation VALUES ("{}","{}",{})'.format(keyword, name, coords))


def create_trip(keyword, location_name, user, date):
    '''
    Create trip from location's go next 
    '''

    # Get all associated go nexts with location
    cur.execute('''
                SELECT next_name, next_coords 
                FROM Location Go Next 
                WHERE source_name={}
                '''.format(location_name))
    rv = cur.fetchall()
    if not rv:
        raise ValueError('Location with coordinates {} does not exist'.format(location_coordinates))

    # Get info and create location for all go nexts
    locations = []
    for location in rv:
        new_location = get_location_by_name(location[0])
        create_trip_location(keyword, location[1], location[0])
        locations.append(location_to_dict(new_location));
    
    cur.execute('''
                INSERT INTO Trip
                VALUES ("{}", "{}", {})
                '''.format(user, keyword, date))
     
    return locations 


def location_to_dict(location):
    location_dict = {'coords':location[0], 'description':location[1], 
                     'eat':location2[2], 'see':location[3], 'do':location[4],
                     'name':location[5]}
    return location_dict
    
