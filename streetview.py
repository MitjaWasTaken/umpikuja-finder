import os

import requests as r
from json import loads

from secret import key
from utils import sign_url

def getImage(lat, long):
    addr = getAddress(lat, long)
    if os.path.exists(addr): 
        print("Location already exist")
        return
    os.mkdir(addr)

    for heading in range(0,360,45):
        url = f"https://maps.googleapis.com/maps/api/streetview?location={lat},{long}&size=640x640&heading={heading}&key={key}"
        signed_url = sign_url(url)

        fileName = os.path.join(addr, f"{heading}.jpg")

        res = r.get(signed_url)
        with open(fileName, 'wb') as f:
            f.write(res.content)
            f.close()

def getAddress(lat, long):
    baseUrl = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"latlng":f"{lat},{long}","key":key,"language":"fi"}

    res = r.get(baseUrl, params=params)
    if res.status_code == 200:
        address =  loads(res.text)["results"][0]["formatted_address"]
        return address.split(", Suomi")[0]
    return f"{lat},{long}"