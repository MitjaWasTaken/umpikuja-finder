from streetview import getImage, getAddress

from json import loads
from sys import exit

import argparse
import requests as r
import utm
import xlsxwriter

# Argparser configuration
parser = argparse.ArgumentParser(description="Työkalu, jolla voit löytää mahdollisesti hulvattomia umpitiemerkkejä (Kuvissa 100% varmuudella merkki ei kuitenkaan näy :/).")
parser.add_argument("-l", "--lista", help="Listaa osoitteet ja mahdolliset kylttien kuvaukset Exceliin", action="store_true")
parser.add_argument("-k", "--kuva", help="Luo jokaista osoitetta kohden kansion ja yrittää taltioida liikennemerkin Google Street Viewin avulla", action="store_true")
parser.add_argument("-t", "--tyyppi", help="Halutessasi voit etsiä erinäisiä kylttejä käyttämällä tyyppitunnusta, kuten \"A1.1\" mutkalle", type=str, default="F24.2")

args = parser.parse_args()

workbook = None

if args.lista:
    ans = input("Huomaathan, että ohjelma ylikirjoittaa jo olemassa olevan excel tiedoston. Haluatko jatkaa? (k/e): ")
    if ans != "k":
        print("\nNo ei vittu sitte 😢\n")
        exit(1)

    workbook = xlsxwriter.Workbook('output.xlsx')
    worksheet = workbook.add_worksheet()

    bold_format = workbook.add_format()
    bold_format.set_bold()

    worksheet.write("A1", "Osoite", bold_format)
    worksheet.set_column(0, 0, 25)
    worksheet.write("B1", "Kunta/Kaupunki", bold_format)
    worksheet.set_column(1, 1, 20)
    worksheet.write("C1", "Kartalla", bold_format)
    worksheet.write("D1", "Kuvaus", bold_format)
    worksheet.set_column(3, 3, 40)

url = "https://avoinapi.vaylapilvi.fi/vaylatiedot/digiroad/wfs"
params = {"request":"GetFeature","count":20,"cql_filter":f"tyyppi='{args.tyyppi}'","outputFormat":"json","service":"wfs","version":"2.0.0","typeNames":"dr_liikennemerkit"}

res = r.get(url, params=params)

if res.status_code == 200:
    try:
        json = loads(res.text)
        row = 1
        for feature in json["features"]:
            coord_x = feature["geometry"]["coordinates"][0]
            coord_y = feature["geometry"]["coordinates"][1]
            lat, long =  utm.to_latlon(coord_x, coord_y, 35, "N")

            if args.lista:
                addr = getAddress(lat,long).split(", ")[0]
                municipality = getAddress(lat,long).split(", ")[1][6:]
                link = f"https://google.com/maps/search/{lat},{long}"
                desc = feature["properties"]["paamerktxt"]

                worksheet.write(row, 0, addr)
                worksheet.write(row, 1, municipality)
                worksheet.write_url(row, 2, link, string="linkki")
                worksheet.write(row, 3, desc)

                row += 1
            
            if args.kuva:
                getImage(lat,long)
                
    except KeyboardInterrupt:
        if workbook:
            print("Tallenetaan tiedostoa...")
            workbook.close()
        exit(0)

else:
    print(f"Nyt ei saatu väylää kiinne :/ ({res.status_code})")

if workbook:
    workbook.close()