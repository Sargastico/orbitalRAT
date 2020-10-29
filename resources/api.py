import json
import requests

api_baseAddr = "https://api.n2yo.com/rest/v1/satellite"
api_key = "LAAZLY-K8434A-49DTES-4JAD"

category_filter = {
    "Amateur radio": 18,
    "Beidou Navigation System": 35,
    "Brightest": 1,
    "Celestis": 45,
    "CubeSats": 32,
    "Disaster monitoring": 8,
    "Earth resources": 6,
    "Education": 29,
    "Engineering": 28,
    "Experimental": 19,
    "Flock": 48,
    "Galileo": 22,
    "Geodetic": 27,
    "Geostationary": 10,
    "Global Position System (GPS) Constellation": 50,
    "Global Positioning System (GPS) Operational": 20,
    "Globalstar": 17,
    "Glonass Constellation": 51,
    "Glonass Operational": 21,
    "GOES": 5,
    "Gonets": 40,
    "Gorizont": 12,
    "Intelsat": 11,
    "Iridium": 15,
    "IRNSS": 46,
    "ISS": 2,
    "Lemur": 49,
    "Military": 30,
    "Molniya": 14,
    "Navy Navigation Satellite System": 24,
    "NOAA": 4,
    "O3B Networks": 43,
    "OneWeb": 53,
    "Orbcomm": 16,
    "Parus": 38,
    "QZSS": 47,
    "Radar Calibration": 31,
    "Raduga": 13,
    "Russian LEO Navigation": 25,
    "Satellite-Based Augmentation System": 23,
    "Search & rescue": 7,
    "Space & Earth Science": 26,
    "Starlink": 52,
    "Strela": 39,
    "Tracking and Data Relay Satellite System": 9,
    "Tselina": 44,
    "Tsikada": 42,
    "Tsiklon": 41,
    "TV": 34,
    "Weather": 3,
    "Westford Needles": 37,
    "XM and Sirius": 33,
    "Yaogan": 36,
}

def rawJsonInfoRequest(sat_id):

    request_url = api_baseAddr + str(sat_id) + "&apiKey=" + api_key
    resp = requests.get(url=request_url)

    try:
        checkResponse(resp)
    except:
        return None

    return resp

def getSatelliteINFO(sat_id):

    request_url = api_baseAddr + str(sat_id) + "&apiKey=" + api_key
    resp = requests.get(url=request_url)

    try:
        checkResponse(resp)
    except:
        return None

    data = json.loads(resp.text)
    info = data['info']

    return info

def getSatelliteTLE(sat_id):

    request_url = api_baseAddr + str(sat_id) + "&apiKey=" + api_key
    resp = requests.get(url=request_url)

    try:
        checkResponse(resp)
    except:
        return None

    data = json.loads(resp.text)
    info = data['info']
    tle = data['tle']

    return info, tle

def getSatelliteFuturePositions(sat_id, observer_lat, observer_lng, observer_alt, seconds):

    request_path = "/positions/"+sat_id+"/"+observer_lat+"/"+observer_lng+"/"+observer_alt+"/"+seconds+"/&apiKey="+api_key
    request_url = api_baseAddr + request_path
    resp = requests.get(url=request_url)

    try:
        checkResponse(resp)
    except:
        return None

    data = json.loads(resp.text)
    info = data['info']
    positions = data['positions']

    return info, positions

def getVisualPasses(sat_id, observer_lat, observer_lng, observer_alt, days, min_visibility):

    request_path = "/visualpasses/"+sat_id+"/"+observer_lat+"/"+observer_lng+"/"+observer_alt+"/"+days+"/"+min_visibility+"/&apiKey="+api_key
    request_url = api_baseAddr + request_path
    resp = requests.get(url=request_url)

    try:
        checkResponse(resp)
    except:
        return None

    data = json.loads(resp.text)
    info = data['info']
    visualPasses = data['passes']

    return info, visualPasses

def getRadioPasses(sat_id, observer_lat, observer_lng, observer_alt, days, min_elevation):

    request_path = "/radiopasses/"+sat_id+"/"+observer_lat+"/"+observer_lng+"/"+observer_alt+"/"+days+"/"+min_elevation+"/&apiKey="+api_key
    request_url = api_baseAddr + request_path
    resp = requests.get(url=request_url)

    try:
        checkResponse(resp)
    except:
        return None

    data = json.loads(resp.text)
    info = data['info']
    radioPasses = data['passes']

    return info, radioPasses

def getWhatIsAbove(observer_lat, observer_lng, observer_alt, search_radius, category_id):

    request_path = "/above/"+observer_lat+"/"+observer_lng+"/"+observer_alt+"/"+search_radius+"/"+category_id
    request_url = api_baseAddr + request_path
    resp = requests.get(url=request_url)
    try:
        checkResponse(resp)
    except:
        return None

    data = json.loads(resp.text)
    info = data['info']
    above = data['above']

    return info, above


def checkResponse(response):

    if 'error' in response.text:

        text = json.loads(response.text)
        error = text['error']

        raise ApiExceededException(error)

class ApiExceededException(Exception):
    pass