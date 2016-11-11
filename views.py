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
    cur.execute("SELECT * FROM Trip WHERE Keyword={}".format(keyword))
    trip = cur.fetchone()
    if not trip:
        locations = get_best_location(keyword);
        top_result = locations[0]
        trip = create_trip(keyword, top_result[0], "", datetime.datetime.now())


def get_best_location(keyword):
    '''
    Make requests to LostVoyager with the user inputted keyword
    Choose most popular location from request
    Use BeautifulSoup to parse html and extract required info
    Return information needed to make trip and location
    '''
    return 'hello'


def get_location_coords(location_name):
    rv = requests.get('http://maps.googleapis.com/maps/api/geocode/json?address={}&key=AIzaSyCoIJcakxVen5qGdu_PsV_ajdl33qwGskI'.format(location_name))
    data = rv.json()
    coords = data['results']['geometry']['location']
    return (coords['lat'], coords['lng'])


def process_wiki_text(text):
    '''
    Extract pictures, description, eat, see, do, and go next from wiki text
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
    cur.execute('INSERT INTO TripLocation VALUES ({},{},{})'.format(keyword, name, coords))


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
        location_dict = {'coords':new_location[0], 'description':new_location[1], 
                         'eat':new_location2[2], 'see':new_location[3], 'do':new_location[4],
                         'name':new_location[5]}
        create_trip_location(keyword, location[1], location[0])
        locations.append(location_dict);
    
    cur.execute('''
                INSERT INTO Trip
                VALUES ({}, {}, {})
                '''.format(user, keyword, date))
     
