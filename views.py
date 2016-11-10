from __init__ import app, cur 
from flask import render_template
import requests


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
    Make requests to LostVoyager with the user inputted keyword
    Choose most popular location from request
    Use BeautifulSoup to parse html and extract required info
    Return information needed to make trip and location
    '''
    return 'hello'


def get_location(location_coordinates):


def get_location_coords(location_name):
    rv = requests.get('http://maps.googleapis.com/maps/api/geocode/json?address={}&key=AIzaSyCoIJcakxVen5qGdu_PsV_ajdl33qwGskI')
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


def create_trip_location(keyword, coords):
    cur.execute('INSERT INTO TripLocation VALUES ({},{})'.format(keyword, coords))


def create_trip(keyword, location_coordinates, user, date):
    '''
    Create trip from location's go next 
    '''

    # Get all associated go nexts with location
    cur.execute('''SELECT next_name, next_coords 
                   FROM Location Go Next 
                   WHERE source_coords={}'''.format(location_coordinates))
    rv = cur.fetchall()
    if not rv:
        raise ValueError('Location with coordinates {} does not exist'.format(location_coordinates))

    locations = []
    # Get info and create location for all go nexts
    for location in rv:
        location = get_location_by_coords(location[1])
        if not location:
            create_location(location[0], location[1])
        create_trip_location(keyword, location[1])
    
    cur.execute('''
                INSERT INTO Trip
                VALUES ({}, {}, {})
                '''.format(user, keyword, date))
     
    

