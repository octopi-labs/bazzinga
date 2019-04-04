
import json

import requests
from flask import jsonify as _jsonify
from flask import redirect, render_template, request, url_for
from rfc3987 import parse
from shorten import RevokeError
from werkzeug.urls import iri_to_uri

from libapp import app, shortnerd


def jsonify(obj, status_code=200):
    obj['status'] = 'error' if 'error' in obj else 'okay'
    res = _jsonify(obj)
    res.status_code = status_code
    return res


def valid_url(url):
    p = parse(url, rule='URI_reference')
    return all([p['scheme'], p['authority'], p['path']])


@app.route('/shorten', methods=['POST'])
def shorten():
    payload = json.loads(request.data)
    body = payload['body']
    data = body['data']
    url = str(data['url']).strip()
    id_type = str(data['type']).strip()

    if not valid_url(url):
        payload['body'] = {"status": "error",
                           "message": "Not a valid URL: {}".format(str(url,))
                           }
        payload['header'] = {"message": "Invalid URL", "status": "error",
                             "token": payload['header']['token']
                             }
        return jsonify(payload, 400)

    try:
        key, token = shortnerd.insert(url)
        url = url_for('bounce', id_type=id_type, key=key, _external=True)
        revoke = url_for('revoke', token=token, _external=True)

        payload['body'] = {
            "message": "Successfully created short url",
            "status": "success"
        }
        payload['body']['results'] = {
            'key': key,
            'url': url,
            'token': token,
            'revoke': revoke
        }
        payload['header'] = {"message": "Successfully executed command", "status": "success",
                             "token": payload['header']['token']}
        return jsonify(payload)
    except Exception as e:
        payload['body'] = {"status": "error", "message": "{}".format(e)}
        payload['header'] = {"message": "Execution error", "status": "error",
                             "token": payload['header']['token']}
        return jsonify(payload, 400)


@app.route('/status/<key>', methods=['GET'])
def check_status(key):
    """
    Check status of the short url
        :param key: Key of short url
    """
    if key in shortnerd:
        payload = {"status": "success"}
        status_code = 200
    else:
        payload = {"status": 'error', 'error': "{} does not exists".format(key)}
        status_code = 404

    return jsonify(payload, status_code)


@app.route('/<id_type>/<key>', methods=['GET'])
def bounce(id_type, key):
    """
    Bounce / Redirect short url to long url
        :param id_type: Type of request, generally `s` for redirect
        :param key: short url key to redirect to
    """
    query_string = request.query_string
    try:
        uri = shortnerd[key]
        redirect_url = "{url}?{query}".format(
            url=iri_to_uri(uri), query=query_string)
        return redirect(redirect_url)
    except KeyError as e:
        app.logger.error(
            "Exception occured during processing key:{}".format(key))
        app.logger.exception(e)
        return redirect("https://mycuteoffice.com/not-found")


@app.route('/revoke/<token>', methods=['POST'])
def revoke(token):
    """
    Revoke Short url to refresh it
        :param token: Token of short url to identify and revoke
    """
    payload = {}
    try:
        shortnerd.revoke(token)
        payload['body'] = {
            "message": "Successfully removed short url",
            "status": "success"
        }
        payload['header'] = {
            "message": "Successfully executed command",
            "status": "success"
        }
        return jsonify(payload)
    except Exception as e:
        payload['body'] = {"status": "error", "message": "{}".format(e)}
        payload['header'] = {"message": "Execution error", "status": "error"}
        return jsonify(payload)
