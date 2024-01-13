from streetview import getImage, getAddress

from json import loads
from sys import argv, exit

import argparse
import requests as r
import utm
import xlsxwriter

# Argparser configuration
parser = argparse.ArgumentParser(description="Työkalu, jolla voit löytää mahdollisesti hulvattomia umpitiemerkkejä (Kuvissa 100% varmuudella merkki ei kuitenkaan näy :/).")
parser.add_argument("-l", "--lista", help="Listaa osoitteet ja mahdolliset kylttien kuvaukset Exceliin", action="store_true")
parser.add_argument("-k", "--kuva", help="Luo jokaista osoitetta kohden kansion ja yrittää taltioida liikennemerkin Google Street Viewin avulla", action="store_true")

args = parser.parse_args()

workbook = None

if args.lista:
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

        if args.lista:
            addr = getAddress(lat,long)
            desc = feature["properties"]["paamerktxt"]

            worksheet.write(row, 0, addr)
            worksheet.write(row, 1, desc)

            row += 1
        
        if args.kuva:
            getImage(lat,long)

if workbook:
    workbook.close()