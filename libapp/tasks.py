from libapp import app, celeryd
from libapp.sender import publish_msg, subscribe_msg
from libapp.sitemap.sitemap import Sitemap


@celeryd.task(priority=0)
def transform_data(source_q, dest_q):
    if isinstance(source_q, list) and isinstance(dest_q, list):
        for source, dest in zip(source_q, dest_q):
            app.logger.info("{source} > {dest}".format(source=source, dest=dest))
            publish_msg(source, dest)
    else:
        publish_msg(source_q, dest_q)


@celeryd.task(priority=1)
def subscribe_data():
    subscribe_msg()


@celeryd.task(priority=2)
def generate_sitemap():
    Sitemap.create_sitemap_xml_request()
