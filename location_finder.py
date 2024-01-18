from utils import load_exclude_ids, add_id_exclucion, parse_excel_file, append_previous_excel

from json import loads
from sys import exit

import argparse
import requests as r
import utm

# Argparser configuration
parser = argparse.ArgumentParser(description="Find possibly amazing dead-end signs or other traffic signs in Finland", epilog="Mitja Komi 2024")
parser.add_argument("-b", "--budget", help="Budget version, so neither Google Street View photos nor addresses, only coordinates to the output file", action="store_true")
parser.add_argument("-l", "--list", help="List the addresses of traffic signs and possible descriptions in Excel", action="store_true")
parser.add_argument("-o", "--output", metavar="", help="Define the output file; default output.xlsx", default="output.xlsx")
parser.add_argument("-a", "--append", metavar="", help="Define the file that will be appended to the start of the output file; default output.xlsx (Please don't give a file that isn't the output of this program. Not compatible with the output of the budget Excel)", default="output.xlsx")
parser.add_argument("-s", "--street", help="Fetch pictures from Google Street View to folders by addresses (not 100%% accurate due to very good data provided by the Finnish Transport Infrastructure Agency) ", action="store_true")
parser.add_argument("-c", "--count", metavar="n", help="Limit the number of signs to be searched", type=int, default=10)
parser.add_argument("-t", "--type", help="Search any type of sign using a traffic sign type. For example, A1.1 for mutka", type=str, default="F24.2")
parser.add_argument("-p", "--path", help="Define the path where folders by addresses with pictures are stored (requires -s parameter)", type=str)
parser.add_argument("-e", "--exclude", help="Define the file where the ids of traffic signs that will be excluded are saved and the ids of searched signs will be saved", type=str, default="exclude_ids")

args = parser.parse_args()

prev_file = parse_excel_file(args.append)
output_file = parse_excel_file(args.output)
workbook = None
last_row = 1

if not args.budget:
    from streetview import getImage, getAddress
else:
    args.street = args.list = None
    ans = input(f"Take notice that {output_file} will be completely overwritten :) Do you want to proceed? (y/n): ")
    if ans != "y":
        print("\nWell, see you later, alligator 😢\n")
        exit(1)
    print("\n")

    import xlsxwriter
    workbook = xlsxwriter.Workbook(output_file)
    worksheet = workbook.add_worksheet()

    bold_format = workbook.add_format()
    bold_format.set_bold()

    worksheet.write("A1", "Koordinaatit", bold_format)
    worksheet.set_column(0, 0, 15)
    worksheet.write("B1", "Kartalla", bold_format)
    worksheet.write("C1", "Kuvaus", bold_format)
    worksheet.set_column(2, 2, 40)


if not args.list and not args.street and not args.budget:
    print("\nThe --street or the --list parameter is required!\n")
    exit(0) 

if not args.street and args.path:
    print("\nThe --path parameter requires the --street parameter!\n")
    exit(0)


if args.list:
    ans = input(f"Take notice that the {prev_file} will be appended to the top of the {output_file}! Do you want to proceed? (y/n): ")
    if ans != "y":
        print("\nWell, see you later, alligator 😢\n")
        exit(1)
    print("\n")
    
    if not args.budget:
        workbook, worksheet, last_row = append_previous_excel("output.xlsx")       

exclude_ids_filename = args.exclude

def request_data(count):
    url = "https://avoinapi.vaylapilvi.fi/vaylatiedot/digiroad/wfs?service=wfs&version=2.0.0"
    params = {"typeNames":"dr_liikennemerkit", "request":"GetFeature","count":count,"propertyName": "(geom,paamerktxt)", "cql_filter":f"tyyppi='{args.type}'","outputFormat":"json",}

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

        if args.budget:
            coords = f"{round(lat,3)}, {round(long,3)}"
            link = f"https://google.com/maps/search/{lat},{long}"
            desc = feature["properties"]["paamerktxt"]

            worksheet.write(row, 0, coords)
            worksheet.write_url(row, 1, link, string="linkki")
            worksheet.write(row, 2, desc)

            print(f"Added \"{coords}\" to the list!")
            row += 1
        else:
            if args.list:
                addr = getAddress(lat,long).split(", ")[0]
                municipality = getAddress(lat,long).split(", ")[1][6:]
                link = f"https://google.com/maps/search/{lat},{long}"
                desc = feature["properties"]["paamerktxt"]

                worksheet.write(row, 0, addr)
                worksheet.write(row, 1, municipality)
                worksheet.write_url(row, 2, link, string="linkki")
                worksheet.write(row, 3, desc)

                print(f"Added \"{addr}\" to the list!")
                row += 1
            
            if args.street:
                if args.path: getImage(lat,long, filePathOffset=args.path)
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
            print(f"The Finnish Transport Infrastructure Agency didn't answer us correctly :/ ({res.status_code})")
        break

    except KeyboardInterrupt:
        if workbook:
            print(f"Saving {output_file} ...")
            workbook.close()
        exit(0)

if workbook:
    workbook.close()