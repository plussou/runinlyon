import folium
import gpxpy
import requests
BASE_URI = "https://www.metaweather.com"

# Parsing an existing file:
# -------------------------

def overlayGPX(gpxData, zoom):

    gpx_file = open(gpxData, 'r')
    gpx = gpxpy.parse(gpx_file)

    points = []

    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                points.append(tuple([point.latitude, point.longitude]))
                z = point.elevation

    latitude = sum(p[0] for p in points)/len(points)
    longitude = sum(p[1] for p in points)/len(points)

    myMap = folium.Map(location=[latitude,longitude],zoom_start=zoom)
    folium.PolyLine(points, color="red", weight=2.5, opacity=1).add_to(myMap)

    return (myMap)


def get_lat_lon(adresse):
    url="https://api-adresse.data.gouv.fr/search/"
    params={'q':adresse}
    response=requests.get(url,params=params).json()
    lon, lat = response['features'][0]['geometry']['coordinates']
    return (lat,lon)

def get_woeid(lat,lon):
    url = BASE_URI + f"/api/location/search/"
    params = {'lattlong':f'{lat},{lon}'}
    response = requests.get(url,params=params).json()
    return response[0]

