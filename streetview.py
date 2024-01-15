import os

import requests as r
from json import loads

from secret import key
from utils import sign_url

def getImage(lat, long, filePathOffset=""):
    addr = getAddress(lat, long)
    folder = os.path.join(filePathOffset, addr)
    if os.path.exists(folder): 
        print("Location already exist")
        return
    os.makedirs(folder)

    for heading in range(0,360,45):
        url = f"https://maps.googleapis.com/maps/api/streetview?location={lat},{long}&size=640x640&heading={heading}&key={key}"
        signed_url = sign_url(url)

        fileName = os.path.join(folder, f"{heading}.jpg")

        res = r.get(signed_url)
        with open(fileName, 'wb') as f:
            f.write(res.content)
            f.close()
    
    print(f"Koitettiin ladata \"{addr}\":n kyltin kuvat kansioon \"{folder}\"!")

def getAddress(lat, long):
    baseUrl = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"latlng":f"{lat},{long}","key":key,"language":"fi"}

    res = r.get(baseUrl, params=params)
    if res.status_code == 200:
        address =  loads(res.text)["results"][0]["formatted_address"]
        return address.split(", Suomi")[0]
    return f"{lat},{long}"