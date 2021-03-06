#!/usr/bin/env python
"""
VATSIM Status Proxy
Copyright (C) 2017  Pedro Rodrigues <prodrigues1990@gmail.com>

This file is part of VATSIM Status Proxy.

VATSIM Status Proxy is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 2 of the License.

VATSIM Status Proxy is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with VATSIM Status Proxy.  If not, see <http://www.gnu.org/licenses/>.
"""
from requests import get
from datetime import datetime

def import_data(eve_app, url, api_key):
    icao_data = request_icao_data(url, api_key).json()
    proxy_data = parse_icao_data(icao_data)
    populate_data(eve_app, proxy_data)

def populate_data(eve_app, data, replace=False):
    db = eve_app.data.driver.db['firs']
    timestamp = datetime.now();

    if replace:
        db.remove()
        db.insert(data)
    else:
        for document in data:
            existing = db.find_one({'icao': document['icao']})
            if existing:
                del document['callsigns']
                del document['name']
                existing['updated'] = timestamp
                existing.update(document)
                db.save(existing)
            else:
                document['_created'] = timestamp
                document['_updated'] = timestamp
                db.insert_one(document)

def parse_icao_data(icao_data):
    proxy_data = []

    for icao_fir in icao_data:
        proxy_fir = {
            'icao': icao_fir['properties']['ICAOCODE'],
            'name': icao_fir['properties']['FIRname'],
            'callsigns': [
                icao_fir['properties']['ICAOCODE']
            ],
            'location': {
                'type': 'Point',
                'coordinates': [
                    icao_fir['properties']['centlong'],
                    icao_fir['properties']['centlat']
                ]
            },
            'boundaries': {
                'type': 'Polygon',
                'coordinates': []
            }
        }
        if icao_fir['geometry']['type'] == 'Polygon':
            for icao_fir_boundaries in icao_fir['geometry']['coordinates'][0]:
                proxy_fir['boundaries']['coordinates'].append([
                    icao_fir_boundaries[1], # lat
                    icao_fir_boundaries[0]  # lng
                ])
        proxy_data.append(proxy_fir)
    return proxy_data

def request_icao_data(url, api_key):
    parameters = {
        'api_key': api_key,
        'format': 'json',
        'firs': ''
    }
    head = {'Content-Type':'application/json'}
    res = get(url, params=parameters, headers=head)

    return res
