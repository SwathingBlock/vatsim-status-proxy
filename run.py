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
from eve import Eve
from flask import Blueprint, current_app as app
import os
from src import vatsim_data
from src import icao_data
import datetime

app = Eve()
blueprint = Blueprint('prefix_uri', __name__)

# Heroku support: bind to PORT if defined, otherwise default to 5000.
if 'PORT' in os.environ:
    port = int(os.environ.get('PORT'))
    host = '0.0.0.0'
    debug = False
else:
    port = 5000
    host = '0.0.0.0'
    debug = True

def pre_clients_get_callback(request, lookup):
    # check if newer info can be downloaded from vatsim status service
    if vatsim_data.is_data_old_enough(app, 'clients'):
        print('clients called')
        vatsim_data.pull_vatsim_data(app)
    else:
        print('did not update')
def pre_prefile_get_callback(request, lookup):
    # check if newer info can be downloaded from vatsim status service
    if vatsim_data.is_data_old_enough(app, 'prefile'):
        print('prefile called')
        vatsim_data.pull_vatsim_data(app)
    else:
        print('did not update')		
		
app.on_pre_GET_clients += pre_clients_get_callback
app.on_pre_GET_prefile += pre_prefile_get_callback

@blueprint.route('/firs/update', methods=['GET'])
def update_firs():
    icao_data.import_data(app, 'https://v4p4sz5ijk.execute-api.us-east-1.amazonaws.com/anbdata/airspaces/zones/fir-list', '2a877ab0-4ed2-11e7-9b2e-d3182793b831')
    return 'Done'

app.register_blueprint(blueprint)

if __name__ == '__main__':
    app.run(host=host, port=port, debug=debug)
