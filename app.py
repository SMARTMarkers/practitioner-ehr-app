#!/usr/bin/env python3

import jwt
import logging
from prokit import smartclient
from flask import Flask, redirect, session, request, render_template, jsonify
from fhirclient import client
from fhirclient.models import practitioner


app = Flask(__name__, template_folder='app/templates')
app_secret = "applicaitonsecret123"
app.secret_key = app_secret
app.debug = True
app.user_practitioner = None


smart_settings = {
        'app_id'        :       'pro_app2',
        'redirect_uri'  :       'http://127.0.0.1:8000/callback',
        'scope'         :       'openid fhirUser launch launch/patient',
        'app_secret'    :        app_secret,
        'patient_id'    :       '39234650-0229-4aee-975b-c8ee68bab40b'
        }



def _save_state(state):
    session['state'] = state 
    session.modified = True

def _smart_client(): 

    state = session.get('state')
    if state:
        return smartclient.PROClient(state=state, save_func=_save_state)
    else:
        return smartclient.PROClient(settings=smart_settings, save_func=_save_state)

@app.route('/launch.html')
def app_launch(): 
    smart_settings.update({'api_base': request.args.get('iss', '')}) 
    smart = _smart_client()
    if smart.ready and smart.patient is not None:
        return redirect('/index.html')
    else:
        auth_url = smart.authorize_url
        if auth_url:
            return redirect(auth_url) 
        else:
            return msg('error authorizing')


@app.route('/requests/new') 
def request_pgd(): 
    smart = _smart_client()

    instrument_type = request.args.get('instrumenttype')
    instrument_id   = request.args.get('instrumentid')
    if instrument_id is None or instrument_type is None:
        return msg('No')

    instr = None
    if instrument_type == 'webrepository':
        instr = [instr for instr in smart.instrumentlist_devices if instr.identifier == instrument_id][0]
    elif instrument_type == 'activity':
        instr = [instr for instr in smart.instrumentList_activity if instr.identifier == instrument_id][0]
    elif instrument_type == 'survey':
        instr = [instr for instr in smart.instrumentlist_questionnaires if instr.identifier == instrument_id][0]
    elif instrument_type == 'activetask':
        instr = [instr for instr in smart.instrumentlist_activetasks if instr.identifier == instrument_id][0]
    
    print(f'selected instrument is {instr.identifier}')

    if instr is None:
        return msg('No')

    success = smart.dispatchRequest(selected_instrument=instr, practitioner_resource=app.user_practitioner, selected_schedule=None)
    print(success)
    if success:
        return jsonify(result={'result':'success', 'request_id': success.identifier, 'request_title': success.title})
    else:
        return jsonify(result={'result': 'fail'})

@app.route('/index.html')
def app_main():

    smart = _smart_client() 
    print(session['state'])
    if app.user_practitioner is None:
        idtoken = session['state']['launch_context']['id_token']
        if idtoken is None: 
            return msg('id-token not found')
        jwtDecoded = jwt.decode(idtoken, verify=False)
        practitioner_id = jwtDecoded['fhirUser'].split('/')[1]
        app.user_practitioner = smart.user_practitioner(practitioner_id)

    return render_template('index.html', 
            page='request', 
            proclient=smart, 
            observations=smart.getobservations(),
            requests=smart.getrequests(),
            questionnaires=smart.instrumentlist_questionnaires,
            promis=smart.instrumentlist_promis, 
            activetasks=smart.instrumentlist_activetasks,
            activityInstruments=smart.instrumentList_activity,
            healthkit=smart.instrumentlist_healthkit,
            devices=smart.instrumentlist_devices
            )

@app.route('/reset')
def reset():
    _reset()
    return msg('Deleted session')


def _reset():
    if 'state' in session:
        del session['state']



@app.route('/callback')
def auth_callback():
    smart = _smart_client()
    try:
        smart.handle_callback(request.url)
    except Exception as e:
        return """<h1>Authorization Error</h1>{0}""".format(e)
    return redirect('/index.html')


def msg(test):
    return f'{test}'

def log(msg):
    logging.debug(msg)






if '__main__' == __name__:
    logging.basicConfig(level=logging.DEBUG)
    app.run(debug=True, port=8000)
