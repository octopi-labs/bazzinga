from flask import render_template

from libapp import app
from libapp.config import libconf
from libapp.sender import publish_msg
from libapp.tasks import subscribe_data


@app.route("/bazzinga/notify")
def notify():
    subscribe_data.apply_async(queue=libconf.EMAIL_Q, serializer='json')
    return render_template("notify.html")


@app.route("/bazzinga/publisher", methods=["GET", "POST"])
def publisher():
    publish_msg(source_q=libconf.PUB_EMAIL_Q, dest_q=libconf.EMAIL_Q) #.apply_async(serializer='json')
    return render_template("publisher.html")
