import requests
import sys


query = " ".join(sys.argv[1:])
key = 'AIzaSyCoIJcakxVen5qGdu_PsV_ajdl33qwGskI'
rv = requests.get('https://maps.googleapis.com/maps/api/place/autocomplete/json?key={}&input={}&type=geocode&'.format(key, query))
data = rv.json()
if data['status'] == 'OK':
    location = data['predictions'][0]
    place_id = location['place_id']
    rv = requests.get('https://maps.googleapis.com/maps/api/place/details/json?key={}&placeid={}'.format(key, place_id))
    data = rv.json()['result']
    photo_ref = data['photos'][0]['photo_reference']
    url = 'https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={}&key={}'.format(photo_ref, key)
    print url
    
