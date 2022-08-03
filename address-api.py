from flask import Flask, render_template, request, jsonify
import sqlite3
from pyproj import CRS, Transformer

app = Flask(__name__, static_url_path='')

@app.route('/')
def hello_world():
    return 'use the following path (SQL wildcards like % are supported, add ?map for a map, or ?json for json): /ADRESSE/<zustellort>/<strassenname>/<hnr>'

@app.route('/ADRESSE/<zustellort>/<strassenname>/<hnr>')
def ADRESSE(zustellort='', strassenname='', hnr=''):
    param_json = request.args.get('json')
    param_map = request.args.get('map')

    if(param_map is not None):
        return render_template('map.html')

    con = sqlite3.connect('data.db')
    con.row_factory = sqlite3.Row

    cur = con.cursor()
    cur.execute('select * from view_adresse where ZUSTELLORT like :zustellort and STRASSENNAME like :strassenname and HNR_ADR_ZUSAMMEN like :hnr', {"zustellort": zustellort, "strassenname": strassenname, "hnr": hnr})

    rows = cur.fetchall()
    res = [dict(row) for row in rows]
    # we want the coordinates in EPSG:4326 (lat/lng as in GPS)
    target_crs = CRS("EPSG:4326")
    # the BEV data uses three different CRSs (EPSG:31256, EPSG:31255, and EPSG:31254)
    # the epsg-number is in the corresponding column
    for row in res:
        from_crs = CRS(row['EPSG'])
        transformer = Transformer.from_crs(from_crs, target_crs)
        row['epsg4326'] = transformer.transform(row['HW'], row['RW'])

    if(param_json is not None):
        return jsonify(res)
    return render_template('adresse.html', rows=res)


if __name__ == '__main__':
    app.run(debug=True)
