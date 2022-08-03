# BEV Address API PoC

This is a proof of concept API to the address data of the BEV (Bundesamt für Eich- und Vermessungswesen).

## Getting Started

Create a python virtual environment and activate it.

```
python -m venv venv
source venv/bin/activate
```

## Download and import address data

Install the dependencies for the importer.

```
pip install requests pandas 
```

Run the importer to download the address data and import it into a sqlite database.

```
python import-data.py
```

## Run the Flask application

Install the dependencies for the Flask application

```
pip install flask pyproj
```

Run the application (for local debug only!)

```
python address-api.py
```

Open a browser and point it to `http://localhost:5000/ADRESSE/<zustellort>/<strassenname>/<hnr>`, append `?json` or `?map` for different representations.
The placeholders allow for SQL wildcards (like %).

Examples:

http://localhost:5000/ADRESSE/Gutenberg-Stenzengreith/Garrach/100

http://localhost:5000/ADRESSE/Gutenberg-Stenzengreith/Garrach/100?json

http://localhost:5000/ADRESSE/G%/Garrach/100?map


## Caveats

* The flask application is *not* production-ready.
* The SQL-queries in the backend are not LIMITed. Be careful with wildcards.
* The backend uses the "ZUSTELLORT" which is sometimes an abbreviated version of the "GEMEINDENAME" (eg. "St.Ruprecht/Raab" vs. "Sankt Ruprecht an der Raab")
* Multiple results will add multiple markers in the map views which will not necessarily all be visible. The maps are centered on the first result.
* The backend uses the "Zustellkoordinate" which, by definition, does not necessarily lie within the corresponding building. Join with the GEBAEUDE table on ADRCD and use the coordinates there if needed (Attention: There are addresses with more than 100 associated "buildings").

