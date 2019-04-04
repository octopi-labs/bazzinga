from libapp import app
from libapp.sitemap.sitemap import Sitemap

from flask import render_template


@app.route("/generate-sitemap", methods=['GET', 'POST'])
def generate_sitemap():
    """
    """
    Sitemap.create_sitemap_xml_request()
    return render_template("sitemap.html")