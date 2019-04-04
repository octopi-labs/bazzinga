# import requests
from flask import render_template

from libapp import app, shortnerd


@app.route('/', methods=['GET', 'POST'])
def index():
    '''
    data = {}
    data['header'] = {'token': ""}
    data['body'] = {}
    data['body']['data'] = {'url': "https://mycuteoffice.com", "type": "s"}
    res = requests.post("http://localhost:9001/shorten", data=json.dumps(data))
    if res.ok:
        payload = json.loads(res.content)
    else:
        payload = {"url": "NOT FOUND", "revoke":"NOT POSSIBLE"}
    '''
    return render_template("index.html")  #, payload=payload)
