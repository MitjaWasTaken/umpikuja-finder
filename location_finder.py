from streetview import getImage, getAddress

from json import loads
from sys import argv, exit

import requests as r
import utm
import xlsxwriter

workbook = None

onlyList = False
if len(argv) > 1:
    if argv[1]=="lista": onlyList = True


if onlyList:
    ans = input("Huomaathan, että ohjelma ylikirjoittaa jo olemassa olevan excel tiedoston. Haluatko jatkaa? (k/e): ")
    if ans != "k":
        print("\nNo ei vittu sitte 😢\n")
        exit(1)

    workbook = xlsxwriter.Workbook('output.xlsx')
    worksheet = workbook.add_worksheet()

    worksheet.write("A1", "Osoite")
    worksheet.set_column(0, 0, 60)
    worksheet.write("B1", "Kuvaus")
    worksheet.set_column(1, 1, 40)

url = "https://avoinapi.vaylapilvi.fi/vaylatiedot/digiroad/wfs"

params = {"request":"GetFeature","count":20,"cql_filter":"tyyppi='F24.2'","outputFormat":"json","service":"wfs","version":"2.0.0","typeNames":"dr_liikennemerkit"}

res = r.get(url, params=params)

if res.status_code == 200:
    json = loads(res.text)
    row = 1
    for feature in json["features"]:
        coord_x = feature["geometry"]["coordinates"][0]
        coord_y = feature["geometry"]["coordinates"][1]
        lat, long =  utm.to_latlon(coord_x, coord_y, 35, "N")

        if onlyList:
            addr = getAddress(lat,long)
            desc = feature["properties"]["paamerktxt"]

            worksheet.write(row, 0, addr)
            worksheet.write(row, 1, desc)

            row += 1
        
        else:
            getImage(lat,long)

if workbook:
    workbook.close()