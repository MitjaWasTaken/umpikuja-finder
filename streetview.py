import os

import requests as r
# from urllib.request import urlretrieve

from json import loads

# !! Ei näin D:
key = "AIzaSyDhEprZ4EPre4MAyofRCup3JqjZvT2CQ-Y"

def getImage(lat, long):
    addr = getAddress(lat, long)
    if os.path.exists(addr): 
        print("Location already exist")
        # print(f"{lat} : {long}")
        return
    os.mkdir(addr)

    urlNorth = f"https://maps.googleapis.com/maps/api/streetview?location={lat},{long}&size=1800x300&fov=180&heading=0&key={key}"
    urlEast = f"https://maps.googleapis.com/maps/api/streetview?location={lat},{long}&size=1800x300&fov=180&heading=90&key={key}"
    urlSouth = f"https://maps.googleapis.com/maps/api/streetview?location={lat},{long}&size=1800x300&fov=180&heading=180&key={key}"
    urlWest = f"https://maps.googleapis.com/maps/api/streetview?location={lat},{long}&size=1800x300&fov=180&heading=270&key={key}"



    northFile = os.path.join(addr, "north.jpg")
    eastFile = os.path.join(addr, "east.jpg")
    southFile = os.path.join(addr, "south.jpg")
    westFile = os.path.join(addr, "west.jpg")

    res = r.get(urlNorth)
    with open(northFile, 'wb') as f:
        f.write(res.content)
        f.close()

    res = r.get(urlEast)
    with open(eastFile, 'wb') as f:
        f.write(res.content)
        f.close()

    res = r.get(urlSouth)
    with open(southFile, 'wb') as f:
        f.write(res.content)
        f.close()

    res = r.get(urlWest)
    with open(westFile, 'wb') as f:
        f.write(res.content)
        f.close()

    # urlretrieve(urlNorth, northFile)
    # urlretrieve(urlSouth, southFile)
    
def getAddress(lat, long):
    baseUrl = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"latlng":f"{lat},{long}","key":key,"language":"fi"}

    res = r.get(baseUrl, params=params)
    if res.status_code == 200:
        address =  loads(res.text)["results"][0]["formatted_address"]
        return address.split(", Suomi")[0]
    return f"{lat},{long}"

if __name__ == "__main__":
    getImage(61.175,22.700)