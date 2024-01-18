from utils import load_exclude_ids, add_id_exclucion, append_previous_excel

from json import loads
from sys import exit

import argparse
import requests as r
import utm

# Argparser configuration
parser = argparse.ArgumentParser(description="Työkalu, jolla voit löytää mahdollisesti hulvattomia umpitiemerkkejä (Kuvissa 100% varmuudella merkki ei kuitenkaan näy :/).", epilog="Mitja Komi 2024")
parser.add_argument("-b", "--budjetti", help="Budjetti versio elikkäs ei mitään Google höttöä vaan listaa ainoastaan kyltin koordinaatit (Ei kuvia)", action="store_true")
parser.add_argument("-l", "--lista", help="Listaa osoitteet ja mahdolliset kylttien kuvaukset exceliin.", action="store_true")
parser.add_argument("-k", "--kuva", help="Luo jokaista osoitetta kohden kansion ja yrittää taltioida liikennemerkin Google Street Viewin avulla", action="store_true")
parser.add_argument("-c", "--count", metavar="n", help="Rajoittaa kuinka monta merkkiä haetaan", type=int, default=10)
parser.add_argument("-t", "--tyyppi", help="Halutessasi voit etsiä erinäisiä kylttejä käyttämällä tyyppitunnusta, kuten \"A1.1\" mutkalle", type=str, default="F24.2")
parser.add_argument("-p", "--polku", help="Halutessasi voit antaa polun kansioon, jonka sisälle kansiot osotteista tallennetaan (Vaatii -k argumentin)", type=str)
parser.add_argument("-e", "--exclude", help="Halutessasi voit itse määrittää tiedoston, jossa on/johon listataan jo läpikäytyjen kylttien tunnisteet", type=str, default="exclude_ids")

args = parser.parse_args()

workbook = None
last_row = 1

if not args.budjetti:
    from streetview import getImage, getAddress
else:
    args.kuva = args.lista = None
    ans = input("Huomaathan, että budjetti argumentti tuhoaa output.xlsx tiedoston täysin :). Haluatko jatkaa? (k/e): ")
    if ans != "k":
        print("\nNo ei vittu sitte 😢\n")
        exit(1)
    print("\n")

    import xlsxwriter
    workbook = xlsxwriter.Workbook('output.xlsx')
    worksheet = workbook.add_worksheet()

    bold_format = workbook.add_format()
    bold_format.set_bold()

    worksheet.write("A1", "Koordinaatit", bold_format)
    worksheet.set_column(0, 0, 15)
    worksheet.write("B1", "Kartalla", bold_format)
    worksheet.write("C1", "Kuvaus", bold_format)
    worksheet.set_column(3, 3, 40)


if not args.lista and not args.kuva and not args.budjetti:
    print("\nArgumentti --kuva tai --lista tarvitaan ohjelman suorittamiseksi!\n")
    exit(0) 

if not args.kuva and args.polku:
    print("\n--polku argumentti vaatii --kuva argumentin!\n")
    exit(0)


if args.lista:
    ans = input("Huomaathan, että ohjelma output.xlsx tiedoston löytyessä lisää listan sen rivien perään. Haluatko jatkaa? (k/e): ")
    if ans != "k":
        print("\nNo ei vittu sitte 😢\n")
        exit(1)
    print("\n")
    
    if not args.budjetti:
        workbook, worksheet, last_row = append_previous_excel("output.xlsx")       

exclude_ids_filename = args.exclude

def request_data(count):
    url = "https://avoinapi.vaylapilvi.fi/vaylatiedot/digiroad/wfs?service=wfs&version=2.0.0"
    params = {"typeNames":"dr_liikennemerkit", "request":"GetFeature","count":count,"propertyName": "(geom,paamerktxt)", "cql_filter":f"tyyppi='{args.tyyppi}'","outputFormat":"json",}

    return r.get(url, params=params)

def handle_data(data, last_row, exclude_ids):
    found = 0
    row = last_row

    ids_to_be_excluded = []
    for feature in data["features"]:
        id =  feature["properties"]["id"]
        if id in exclude_ids:
            continue

        coord_x = feature["geometry"]["coordinates"][0]
        coord_y = feature["geometry"]["coordinates"][1]
        lat, long =  utm.to_latlon(coord_x, coord_y, 35, "N")

        if args.budjetti:
            coords = f"{round(lat,3)}, {round(long,3)}"
            link = f"https://google.com/maps/search/{lat},{long}"
            desc = feature["properties"]["paamerktxt"]

            worksheet.write(row, 0, coords)
            worksheet.write_url(row, 1, link, string="linkki")
            worksheet.write(row, 2, desc)

            print(f"Lisättiin \"{coords}\" listaan!")
            row += 1
        else:
            if args.lista:
                addr = getAddress(lat,long).split(", ")[0]
                municipality = getAddress(lat,long).split(", ")[1][6:]
                link = f"https://google.com/maps/search/{lat},{long}"
                desc = feature["properties"]["paamerktxt"]

                worksheet.write(row, 0, addr)
                worksheet.write(row, 1, municipality)
                worksheet.write_url(row, 2, link, string="linkki")
                worksheet.write(row, 3, desc)

                print(f"Lisättiin \"{addr}\" listaan!")
                row += 1
            
            if args.kuva:
                if args.polku: getImage(lat,long, filePathOffset=args.polku)
                else: getImage(lat,long)

        ids_to_be_excluded.append(id)
        found += 1
        
    if len(ids_to_be_excluded)>0:
        add_id_exclucion(ids_to_be_excluded, exclude_ids_filename)

    return found, row

already = 0
while already != args.count:
    try:
        exclude_ids = load_exclude_ids(exclude_ids_filename)    
        need = len(exclude_ids)+args.count-already
        res = request_data(need)

        if res.status_code == 200:
            already, last_row = handle_data(loads(res.text), last_row, exclude_ids)

        else:
            print(f"Nyt ei saatu väylää kiinne :/ ({res.status_code})")
        break

    except KeyboardInterrupt:
        if workbook:
            print("Tallenetaan tiedostoa...")
            workbook.close()
        exit(0)

if workbook:
    workbook.close()