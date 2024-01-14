from streetview import getImage, getAddress
from utils import load_exclude_ids, add_id_exclucion, append_previous_excel

from json import loads
from sys import exit

import argparse
import requests as r
import utm

# Argparser configuration
parser = argparse.ArgumentParser(description="Työkalu, jolla voit löytää mahdollisesti hulvattomia umpitiemerkkejä (Kuvissa 100% varmuudella merkki ei kuitenkaan näy :/).", epilog="Mitja Komi 2024")
parser.add_argument("-l", "--lista", help="Listaa osoitteet ja mahdolliset kylttien kuvaukset exceliin.", action="store_true")
parser.add_argument("-k", "--kuva", help="Luo jokaista osoitetta kohden kansion ja yrittää taltioida liikennemerkin Google Street Viewin avulla", action="store_true")
parser.add_argument("-c", "--count", metavar="n", help="Rajoittaa kuinka monta merkkiä haetaan", type=int, default=10)
parser.add_argument("-t", "--tyyppi", help="Halutessasi voit etsiä erinäisiä kylttejä käyttämällä tyyppitunnusta, kuten \"A1.1\" mutkalle", type=str, default="F24.2")

args = parser.parse_args()

if not args.lista and not args.kuva:
    print("\nArgumentti --kuva tai --lista tarvitaan ohjelman suorittamiseksi!\n")
    exit(0) 

workbook = None
last_row = 0

if args.lista:
    ans = input("Huomaathan, että ohjelma output.xlsx tiedoston löytyessä lisää listan sen rivien perään. Haluatko jatkaa? (k/e): ")
    if ans != "k":
        print("\nNo ei vittu sitte 😢\n")
        exit(1)
    print("\n")

    workbook, worksheet, last_row = append_previous_excel("output.xlsx")

exclude_ids_filename = "exclude_ids"

def request_data(count):
    url = "https://avoinapi.vaylapilvi.fi/vaylatiedot/digiroad/wfs?service=wfs&version=2.0.0"
    params = {"typeNames":"dr_liikennemerkit", "request":"GetFeature","count":count,"propertyName": "(geom,paamerktxt)", "cql_filter":f"tyyppi='{args.tyyppi}'","outputFormat":"json",}

    return r.get(url, params=params)

def handle_data(data, last_row, exclude_ids):
    leftover = 0
    found = 0
    row = last_row

    try:
        for feature in data["features"]:
            id =  feature["properties"]["id"]
            if id in exclude_ids:
                leftover += 1
                continue

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

                print(f"Added \"{addr}\" to list!")
                row += 1
            
            if args.kuva:
                getImage(lat,long)

            add_id_exclucion(id, exclude_ids_filename)
            found += 1
        
        return leftover, found, row
    
    except KeyboardInterrupt:
        if workbook:
            print("Tallenetaan tiedostoa...")
            workbook.close()
        exit(0)


still_need = args.count
offset = 0
already = 0
while already < args.count:
    exclude_ids = load_exclude_ids(exclude_ids_filename) 
    offset = len(exclude_ids)-1
    res = request_data(still_need+offset)
    

    if res.status_code == 200:
        still_need, already, last_row = handle_data(loads(res.text), last_row, exclude_ids)
        
    else:
        print(f"Nyt ei saatu väylää kiinne :/ ({res.status_code})")
        break

if workbook:
    workbook.close()