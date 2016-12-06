from __init__ import app, cur, conn
from flask import render_template, redirect, request
import requests
import datetime
import sys
from bs4 import BeautifulSoup
import urllib2

url = 'http://fa16-cs411-47.cs.illinois.edu'


@app.route('/', methods=['GET', 'POST'])
def welcome_user():
    if request.method == 'GET':
        return render_template('webpage2/welcome-form/welcome.html')
    else:
	username = request.form.get('username', None)
        password = request.form.get('password', None)
        if request.args.get("login", None):
            valid_login = username and password and authenticated(username, password)
            if valid_login:
                return redirect(url + "/{}/search".format(username))
            else:
                return render_template('webpage2/welcome-form/welcome.html', login_failed=True)

        elif request.args.get("signup", None):
            name = request.form.get('name', None)
            valid_signup = username and password and name and create_user(username, password, name)
            if valid_signup:
                return redirect(url + "/{}/search".format(username))
            else:
                return render_template('webpage2/welcome-form/welcome.html', login_failed=True)


@app.route('/<username>/logout')
def logout_user(username):
    change_user_logged_in(username, False)
    return redirect(url)


@app.route('/<username>/search')
def search(username):
    if not authenticated(username):
        return redirect(url)

    return render_template('webpage2/search.html', username=username)


@app.route('/example_query')
def example_query():
    cur.execute("SELECT page_title FROM page WHERE page_title LIKE '%Republic%'")
    query_name = "SELECT page_title FROM page WHERE page_title LIKE '%Republic%'"
    query = str(cur.fetchall())
    return render_template('example_query.html', query_name=query_name, query=query)


@app.route('/<username>/search/<keyword>/<lpnum>', methods=['GET'])
def get_trip(username, keyword, lpnum):
    if not authenticated(username):
        return render_templated('webpage2/welcome-form/welcome.html', login_failed=True)
    '''
    location1 = cur.execute("SELECT * FROM Location WHERE Name='Martinique'")
    location1 = list(cur.fetchone())
    location1.append("http://www.airtransat.com/getmedia/8304aca5-8ca0-4aa0-976d-cf11442d7871/Fort-de-France-thumbnail.jpg?width=515")
    location2 = cur.execute("SELECT * FROM Location WHERE Name='Nicaragua'")
    location2 = list(cur.fetchone())
    location2.append('http://servicesaws.iadb.org/wmsfiles/images/0x0/nicaragua-32899.jpg')
    location3 = cur.execute("SELECT * FROM Location WHERE Name='Thailand'")
    location3 = list(cur.fetchone())
    location3.append('http://newmedia.thomson.co.uk/live/vol/0/921d4b57639916341dfa76e38310ff7bc13b11e2/1080x608/web/ASIAFAREASTTHAILANDTHAILANDDES_000423KHAOLAKRES_002378.jpg')
    location4 = cur.execute("SELECT * FROM Location WHERE Name='Samoa'")
    location4 = list(cur.fetchone())
    location4.append('https://lonelyplanetimages.imgix.net/mastheads/GettyImages-167450923_full.jpg?sharp=10&vib=20&w=1200')
    location5 = cur.execute("SELECT * FROM Location WHERE Name='Panama'")
    location5 = list(cur.fetchone())
    location5.append('http://www.total.com/sites/default/files/styles/carrefour/public/thumbnails/image/panama.jpg')
    trip = [location1, location2, location3, location4, location5]
    names = ['Chicago', 'Chicago', 'Chicago', 'Chicago', 'Chicago']
    coords = []
    for location in names:
        coords.append(get_location_coords(location))
    trip = [location_to_dict(location) for location in trip]  
    return render_template('webpage2/trip.html', trip=trip, coords=coords, keyword=keyword, liked=False)
    '''
    

    possible_locations = get_best_locations(keyword)
    lpnum = min(int(lpnum), len(possible_locations))
    has_go_nexts = False
    for location in possible_locations[lpnum:]:
        go_nexts = get_location_go_nexts(location)
        if go_nexts and go_nexts[0][0] != 'EMPTY':
            has_go_nexts = True
            break
        lpnum += 1

    if not has_go_nexts:
        return redirect(url + "/{}/search".format(username))

    trip_exists = get_trip_by_keyword(keyword, lpnum) != None
    if not trip_exists:
        best_location = possible_locations[lpnum]
        best_location = best_location.replace(" ", "_")
        create_trip(keyword, best_location, username, lpnum)
    #raise Exception("CREATED TRIP HERE")
    create_trip_user(keyword, username, lpnum)
    #raise Exception("CREATED TRIP USER HERE")
    trip = get_trip_locations(keyword, lpnum)
    #raise Exception("GOT TRIP DICTS HERE: {}".format(trip))

    '''
    coords = []
    names = [location['name'] for location in trip]
    for location in trip:
        coords.append(get_location_coords(location['name']))
    '''

    liked = get_trip_user(keyword, username, lpnum)[3]
    return render_template('webpage2/trip.html', trip=trip, coords=None, keyword=keyword, liked=liked, username=username, lpnum=lpnum)


@app.route('/<username>/search/<keyword>/<lpnum>/<like>')
def like_trip(username, keyword, lpnum, like):
    like = like == 'True'
    cur.execute('''
                UPDATE TripUser
                SET Assessment={}
                WHERE TripKeyword='{}' AND Username='{}' AND LPNum={}
                '''.format(like, keyword, username, lpnum))

    conn.commit()
    return redirect("{}/{}/search/{}/{}".format(url, username, keyword, lpnum))


@app.route('/<username>/search/<keyword>/<lpnum>/delete')
def delete_past_trip(username, keyword, lpnum):
    cur.execute('''
                DELETE FROM TripUser
                WHERE Username='{}' AND TripKeyword='{}' AND LPNum={}
                '''.format(username, keyword, lpnum))
    conn.commit()
    profile_url = "{}/{}".format(url, username) 
    return redirct(profile_url)


@app.route('/<username>')
def get_user_profile(username):
    return render_template('webpage2/profile.html', recommended=recommend_trip(username), past=past_trips(username))		


def authenticated(username, password=None):
    user = get_user_by_username(username)
    if not user:
        return False

    user_password = user[1]
    logged_in = user[3]

    if not password and logged_in:
        return True
    elif user_password == password:
        change_user_logged_in(username, True)
        return True
    else:
        return False


def get_best_locations(keyword):
    '''
    Make requests to LostVoyager API with the user inputted keyword
    Choose most popular locations from request
    Return information needed to make trip and location AND IMAGE URL
    '''

    destinations = []

    keyword = urllib2.quote(keyword)
    url = "https://www.viator.com/search/"+keyword
    response = urllib2.urlopen(url)
    soup=BeautifulSoup(response.read(), "lxml")

    content = soup.find_all("p", class_="man mts note xsmall")
    for c in content:
        result = str(c)
        split = result.split(',')
        if len(split) > 1:
            result = split[-1]
        else:
            result = split[0]
        result = result.split('<')[0]
        result = result.strip()

        #result = result[result.index(',')+2:]
        #result = result[:result.index('<')-1]
        destinations.append(result)
       
    dests = set() 
    unique_destinations = []
    for location in destinations:
        if location not in dests:
            unique_destinations.append(location)
            dests.add(location)            

    return unique_destinations


def get_trip_locations(keyword, lpnum):
    cur.execute('''
                SELECT LocationName 
                FROM TripLocation 
                WHERE TripKeyword='{}' AND LPNum={}
                '''.format(keyword, lpnum))

    trip_locations = cur.fetchall()
    #raise Exception("Trip location names: {}".format(trip_locations))
    locations = [get_location_by_name(loc[0]) for loc in trip_locations]
    return locations


def get_trip_by_keyword(keyword, lpnum):
    cur.execute("SELECT * FROM Trip WHERE Keyword='{}' AND LPNum='{}'".format(keyword, lpnum))
    trip = cur.fetchone()
    return trip


def get_location_coords(location_name):
    rv = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address={}&key=AIzaSyCoIJcakxVen5qGdu_PsV_ajdl33qwGskI'.format(location_name))
    data = rv.json()
    coords = data['results'][0]['geometry']['location']
    return (coords['lat'], coords['lng'])


def create_location_image(location_name):
    cur.execute("SELECT * FROM Photo WHERE LocationName='{}'".format(location_name))
    photo = cur.fetchone()
    if photo:
        return

    key = 'AIzaSyCoIJcakxVen5qGdu_PsV_ajdl33qwGskI'
    rv = requests.get('https://maps.googleapis.com/maps/api/place/autocomplete/json?key={}&input={}&type=geocode&'.format(key, location_name))
    data = rv.json()
    if data['status'] != 'OK':
        return

    location = data['predictions'][0]
    place_id = location['place_id']
    rv = requests.get('https://maps.googleapis.com/maps/api/place/details/json?key={}&placeid={}'.format(key, place_id))
    data = rv.json()['result']
    if 'photos' not in data:
        url = None
    else:
        photo_ref = data['photos'][0]['photo_reference']
        url = 'https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={}&key={}'.format(photo_ref, key)

    cur.execute("INSERT INTO Photo VALUES ('{}', '{}')".format(url, location_name))
    conn.commit()


def get_location_by_name(name):
    cur.execute('''
                SELECT l.Description, l.Eat, l.See, l.Do, l.Name, p.URL
                FROM Location l, Photo p
                WHERE l.Name='{}' AND p.LocationName = '{}'
                '''.format(name, name))
    location = cur.fetchone()

    if location:
        return location_to_dict(location)
    return None


def get_location_by_coords(coords):
    cur.execute("SELECT * FROM Location WHERE Coordinates='{}'".format(coords))
    location = cur.fetchone()
    return location


def create_trip_location(keyword, location_name, lpnum):
    cur.execute("INSERT INTO TripLocation VALUES ('{}','{}', {})".format(keyword, location_name, lpnum))
    conn.commit()


def create_trip_user(keyword, username, lpnum):
    trip_user = get_trip_user(keyword, username, lpnum)
    if not trip_user:
        cur.execute("INSERT INTO TripUser VALUES ('{}','{}', {}, 0)".format(keyword, username, lpnum))
        conn.commit()


def get_trip_user(keyword, username, lpnum):
    cur.execute("SELECT * FROM TripUser WHERE TripKeyword='{}' AND Username='{}' AND LPNum={}".format(keyword, username, lpnum))
    trip_user = cur.fetchone()
    return trip_user


def create_user(username, password, name):
    user = get_user_by_username(username)
    if user:
        return False
    else:
        cur.execute("INSERT INTO User VALUES ('{}', '{}', '{}', {})".format(username, password, name, True))
	conn.commit()
        return True


def get_user_by_username(username):
    cur.execute("SELECT * FROM `User` WHERE Username='{}'".format(username))
    return cur.fetchone()


def change_user_logged_in(username, logged_in):
    cur.execute("UPDATE User SET LoggedIn={} WHERE Username='{}'".format(logged_in, username))
    conn.commit()


def get_location_go_nexts(location_name):
    # Get all associated go nexts with location
    db_location_name = location_name.replace(" ", "_")
    cur.execute('''
                SELECT NextName, NextCoords
                FROM LocationGoNext
                WHERE SourceName LIKE '{}%'
                '''.format(db_location_name))
    rv = cur.fetchall()
    return rv


def create_trip(keyword, location_name, user, lpnum):
    '''
    Create trip from location's go next
    '''
    go_nexts = get_location_go_nexts(location_name)
    if not go_nexts:
        raise ValueError('Location {} does not exist'.format(location_name))

    create_trip_location(keyword, location_name, lpnum)
    create_location_image(location_name)
    # Get info and create location for all go nexts
    num_go_nexts = min(len(go_nexts), 4)
    for location in go_nexts[:num_go_nexts]:
        name = location[0]
        coords = location[1]
        if name:
            create_trip_location(keyword, name, lpnum)
            create_location_image(name)

    # Create trip
    cur.execute('''
                INSERT INTO Trip
                VALUES ('{}', '{}', {})
                '''.format(keyword, location_name, lpnum))
    conn.commit()


def location_to_dict(location):
    location_dict = {'description':location[0],'eat':location[1],
                     'see':location[2], 'do':location[3],
                     'name':location[4].replace("_", " "), 'photo':location[5]}
    return location_dict

def recommend_trip(username):
	cur.execute("SELECT MAX(u1.LPNum) FROM TripUser u1 WHERE u1.Username = '{}' AND u1.TripKeyword='sailing'".format(username))
	raise Exception("Max query: {}".format(cur.fetchall()))
    

	cur.execute('''
			SELECT u.TripKeyword, u.LPNum
			FROM TripUser u
			WHERE u.Assessment = 1 AND u.Username = '{}' AND u.LPNum = (SELECT MAX(u1.LPNum) FROM TripUser u1 WHERE u1.TripKeyword = u.TripKeyword AND u1.Username = u.Username)
			'''.format(username))
			
	rv = cur.fetchall()

	recommended = [[], []];

	if not rv:
		return None
	else:
		for trip_info in rv:
			keyword = trip_info[0]
			lpnum = trip_info[1]
			recommended[0].append("http://fa16-cs411-47.cs.illinois.edu/{}/search/{}/{}".format(username, keyword, lpnum + 1))
			recommended[1].append(keyword + " {}".format(lpnum+1))

	return recommended
		
def past_trips(username):
	cur.execute('''
			SELECT TripKeyword, LPNum
			FROM TripUser
			WHERE Username = '{}'
			'''.format(username))
			
	rv = cur.fetchall()
	
	past = [[], []];
	
	if not rv:
		return None
	else:
		for trip_info in rv:
            		keyword = trip_info[0]
            		lpnum = trip_info[1]
			past[0].append("http://fa16-cs411-47.cs.illinois.edu/{}/search/{}/{}".format(username, keyword, lpnum))
			past[1].append(keyword + " {}".format(lpnum))
			
	return past

