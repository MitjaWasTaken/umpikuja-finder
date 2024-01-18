<div align="center">
    <h1 align="center">Umpitie finder</h1>
    <p align="center">
        Tool to find traffic signs of your need!
        <br />
        <a href="https://github.com/MitjaWasTaken/umpikuja-finder/issues">Report Bug</a>
        ·
        <a href="https://github.com/MitjaWasTaken/umpikuja-finder/issues">Request Feature</a>
    </p>
</div>


## Getting Started

### Prerequisites
Program requires Python to be installed. You can install it from the official site: https://www.python.org/. 

If you wish to setup Google Cloud, you must add the <a href="https://developers.google.com/maps/documentation/streetview/overview">Street View static API</a> and the <a href="https://developers.google.com/maps/documentation/geocoding/overview">Geocoding API</a> to your project. Check below for further migration with the tool!

### Installation
1. Download the source code using git or by downloading it as a zip.
2. Install libraries
```sh
pip install -r requirements.txt
``` 
3. Run the program with flag suitable for your needs
```sh
python location_finder.py -k -l -c 10 -o wou.xlsx
```

#### Google Cloud configuration (Not required with budget mode!)
1. Setup Google Cloud and add the Google Cloud API key to secrets.py
````py
key = "super_secret_key"
````
2. Add <a href="https://developers.google.com/maps/documentation/maps-static/digital-signature">URL signing secret</a> to secret.py.
```py
secret = "super_secret_secret="
```

## Usage
```sh
location_finder.py [-h] [-b] [-l] [-o] [-a] [-s] [-c n] [-t TYPE] [-p PATH] [-e EXCLUDE]
```

### Options:
<pre>
-h, --help            show this help message and exit
-b, --budget          Budget version, so neither Google Street View photos nor addresses, only coordinates to th
output file
-l, --list            List the addresses of traffic signs and possible descriptions in Excel
-o , --output         Define the output file; default output.xlsx
-a , --append         Define the file that will be appended to the start of the output file; default output.xls
(Please don't give a file that isn't the output of this program. Not compatible with the output of the budge
Excel)
-s, --street          Fetch pictures from Google Street View to folders by addresses (not 100% accurate due to very good data provided by the Finnish Transport Infrastructure Agency)
-c n, --count n       Limit the number of signs to be searched
-t TYPE, --type TYPE  Search any type of sign using a traffic sign type. For example, A1.1 for mutka
-p PATH, --path PATH  Define the path where folders by addresses with pictures are stored (requires -s parameter)
-e, --exclude         Define the file where the ids of traffic signs that will be excluded are saved and the ids of searched signs will be saved

Mitja Komi 2024
</pre>