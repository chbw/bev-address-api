import csv, sqlite3
import hashlib
import requests
import zipfile
import pandas
from os.path import exists
from os import remove

url = 'https://data.bev.gv.at/download/Adressregister/Adresse_Relationale_Tabellen_Stichtagsdaten_20230415.zip'
sha256sum = '6e6d93c48f10a08bb619ed035a628843123f59b02779f2dbfae35712a7eeda4e'
zip_file = 'data.zip'
data_dir = "data"

print('checking for data file')

if(not exists(zip_file)):
    print('data file not found, starting download')
    myfile = requests.get(url)
    open(zip_file, 'wb').write(myfile.content)
    print('data downloaded')

print('verify data file')

with open(zip_file, 'rb') as f:
    bytes = f.read()
    readable_hash = hashlib.sha256(bytes).hexdigest()
    print(readable_hash)
    if(readable_hash == sha256sum):
        print('hash matches')
    else:
        print('hash not matching')
        print('maybe the data source has been updated. check and, if necessary, update hash value or code accordingly')
        exit

print('extract data file')

try:
    with zipfile.ZipFile(zip_file) as z:
        z.extractall(data_dir)
    print("extracted files")
except:
    print("extract failed")
    exit

print('import data to sqlite database')

if(exists('data.db')):
    remove('data.db')

con = sqlite3.connect('file:data.db', uri=True)

tables = ['ADRESSE_GST', 'ADRESSE', 'GEBAEUDE_FUNKTION', 'GEBAEUDE', 'GEMEINDE', 'ORTSCHAFT', 'STRASSE', 'ZAEHLSPRENGEL']
for t in tables:
    print('importing ' + t)
    df = pandas.read_csv(data_dir + '/' + t + '.csv', sep=';', low_memory=False)
    df.to_sql(t, con, if_exists='replace', index=False)

print('import finished')

print('creating indices')

cur = con.cursor()
cur.execute('CREATE INDEX "idx_adresse_gkz" ON "ADRESSE" ("GKZ");')
cur.execute('CREATE INDEX "idx_adresse_okz" ON "ADRESSE" ("OKZ");')
cur.execute('CREATE INDEX "idx_adresse_plz" ON "ADRESSE" ("PLZ");')
cur.execute('CREATE INDEX "idx_adresse_skz" ON "ADRESSE" ("SKZ");')
cur.execute('CREATE INDEX "idx_adresse_hnr" ON "ADRESSE" ("HNR_ADR_ZUSAMMEN");')

cur.execute('CREATE INDEX "idx_gemeinde_gkz" ON "GEMEINDE" ("GKZ");')
cur.execute('CREATE INDEX "idx_gemeinde_gemeindename" ON "GEMEINDE" ("GEMEINDENAME");')

cur.execute('CREATE INDEX "idx_ortschaft_gkz" ON "ORTSCHAFT" ("GKZ");')
cur.execute('CREATE INDEX "idx_ortschaft_okz" ON "ORTSCHAFT" ("OKZ");')
cur.execute('CREATE INDEX "idx_ortschaft_ortsname" ON "ORTSCHAFT" ("ORTSNAME");')

cur.execute('CREATE INDEX "idx_strasse_skz" ON "STRASSE" ("SKZ");')
cur.execute('CREATE INDEX "idx_strasse_STRASSENNAME" ON "STRASSE" ("STRASSENNAME");')
cur.execute('CREATE INDEX "idx_strasse_STRASSENNAMENZUSATZ" ON "STRASSE" ("STRASSENNAMENZUSATZ");')
cur.execute('CREATE INDEX "idx_strasse_SZUSADRBEST" ON "STRASSE" ("SZUSADRBEST");')
cur.execute('CREATE INDEX "idx_strasse_GZK" ON "STRASSE" ("GKZ");')
cur.execute('CREATE INDEX "idx_strasse_ZUSTELLORT" ON "STRASSE" ("ZUSTELLORT");')

print('creating views')

cur.execute('CREATE VIEW "view_adresse" AS SELECT * FROM ADRESSE a INNER JOIN GEMEINDE g ON a.GKZ = g.GKZ INNER JOIN ORTSCHAFT o ON a.OKZ = o.OKZ INNER JOIN STRASSE s ON a.SKZ = s.SKZ')

print('finished')
