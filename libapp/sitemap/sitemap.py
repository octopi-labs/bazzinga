import codecs
import os
from datetime import datetime, time, timedelta
from io import BytesIO
from xml.dom import minidom
from xml.etree.ElementTree import Element, ElementTree, SubElement, tostring

from libapp.config.sitemap import (CITY_URL, DEFAULT_DATE_TIME,
                                   DYNAMIC_SITEMAP_FREQUENCY,
                                   DYNAMIC_SITEMAP_PRIORITY,
                                   LIST_SITEMAP_FREQUENCY,
                                   LIST_SITEMAP_PRIORITY, SITEMAP_DOMAIN,
                                   SITEMAP_REPOSITORY,
                                   STATIC_SITEMAP_FREQUENCY,
                                   STATIC_SITEMAP_PRIORITY, ZONE_URL)
from libapp.enumerator import NodeTypes, SpaceStatus
from libapp.exceptions import BusinessException
from libapp.sitemap.models import (Node, Space, SpaceCategory, SpaceCity,
                                   UrlAlias, Workspace, FileManaged, FileUsage)
from libapp.utils import last_weekday


class Sitemap(object):
    """
    """
    @classmethod
    def create_sitemap_xml_request(cls):
        """Create sitemap.xml file

        :return: Sitemap created
        """
        space_statuses = [SpaceStatus.Published.value, SpaceStatus.Revoked.value,                               SpaceStatus.Filled.value]
        node_types = [item.name.lower() for item in NodeTypes]

        sitemap_list = []
        processed_url_aliases = []
        # Get Sitemap other than spaces, workspaces, users and user blogs
        sitemap_list += get_static_page_sitemap()
        # Get Sitemap for node types
        node_sources = []
        node_changed_dict = {}
        filters = [Node.ntype.in_(node_types)]
        nodes = Node.query.filter(*filters).order_by(Node.ntype.asc()).all()
        if nodes:
            node_sources, node_changed_dict = get_sources(nodes, Node.__name__.lower())
        if node_sources and node_changed_dict:
            _sitemap_list, _processed_url_aliases = generate_sitemap_list(node_sources, node_changed_dict)
            sitemap_list += _sitemap_list
            processed_url_aliases += _processed_url_aliases 
        # Get Sitemap for city
        # Get Sitemap for city/workspace-type
        cities = SpaceCity.query.filter(SpaceCity.status == 1).all()
        city_list = list(set([city.region.lower() for city in cities]))
        categories = SpaceCategory.query.filter(SpaceCategory.category.like("workspace_type")).all()
        category_list = list(set([category.machine_name.replace('_', '-') for category in categories]))
        sitemap_list += get_region_sitemap(city_list, category_list)
        # Get Sitemap for zone
        # Get Sitemap for zone/workspace-type
        # Get sitemap for spaces
        space_sources = []
        space_changed_dict = {}
        filters = [Space.status.in_(space_statuses)]
        spaces = Space.query.filter(*filters).order_by(Space.id.asc()).all()
        if spaces:
            space_sources, space_changed_dict = get_sources(spaces, Space.__name__.lower())
        if space_sources and space_changed_dict:
            _sitemap_list, _processed_url_aliases = generate_sitemap_list(space_sources, space_changed_dict)
            sitemap_list += _sitemap_list
            processed_url_aliases += _processed_url_aliases
        # Get sitemap for workspaces
        workspace_sources = []
        workspace_changed_dict = {}
        workspaces = Workspace.query.join(Space).filter(*filters).order_by(Workspace.id.asc()).all()
        if workspaces:
            workspace_sources, workspace_changed_dict = get_sources(workspaces, Workspace.__name__.lower())
        if workspace_sources and workspace_changed_dict:
            source_images = get_image_list(workspace_sources)
            _sitemap_list, _processed_url_aliases = generate_sitemap_list(workspace_sources, workspace_changed_dict, source_images)
            sitemap_list += _sitemap_list
            processed_url_aliases += _processed_url_aliases
        if sitemap_list:
            xml = generate_xml(sitemap_list)
            if xml:
                sitemap_xml_path = os.path.join(SITEMAP_REPOSITORY, "sitemap.xml")
                sitemap_xml = codecs.open(sitemap_xml_path, 'w', "utf-8")
                sitemap_xml.seek(0)
                sitemap_xml.truncate()
                sitemap_xml.writelines(xml)
                sitemap_xml.close()
        return True


def get_static_page_sitemap():
    """
    """
    sitemap_list = []
    static_content = ["", "login", "user/register", "user/password", "requirement/add",                         "space/add", "blog"]
    for item in static_content:
        record = {
            "loc": "{0}/{1}".format(SITEMAP_DOMAIN, item),
            "priority": STATIC_SITEMAP_PRIORITY,
            "changefreq": STATIC_SITEMAP_FREQUENCY,
            "lastmod": DEFAULT_DATE_TIME.strftime("%Y-%m-%d")
        }
        sitemap_list.append(record)
    return sitemap_list


def get_region_sitemap(region_list, workspace_list):
    """
    """
    sitemap_list = []
    for item in region_list:
        record = {
            "loc": "{0}/{1}/{2}".format(SITEMAP_DOMAIN, CITY_URL, item),
            "priority": LIST_SITEMAP_PRIORITY,
            "changefreq": LIST_SITEMAP_FREQUENCY,
            "lastmod": last_weekday().strftime("%Y-%m-%d")
        }
        sitemap_list.append(record)
        for workspace in workspace_list:
            record = {
                "loc": "{0}/{1}/{2}/{3}".format(SITEMAP_DOMAIN, CITY_URL, item, workspace),
                "priority": LIST_SITEMAP_PRIORITY,
                "changefreq": LIST_SITEMAP_FREQUENCY,
                "lastmod": last_weekday().strftime("%Y-%m-%d")
            }
            sitemap_list.append(record)
    return sitemap_list


def get_region_workspace_sitemap(region_list, workspace_list):
    """
    """
    sitemap_list = []
    for item in region_list:
        for workspace in workspace_list:
            record = {
                "loc": "{0}/{1}/{2}/{3}".format(SITEMAP_DOMAIN, CITY_URL, item, workspace),
                "priority": LIST_SITEMAP_PRIORITY,
                "changefreq": LIST_SITEMAP_FREQUENCY,
                "lastmod": last_weekday().strftime("%Y-%m-%d")
            }
            sitemap_list.append(record)
    return sitemap_list


def get_sources(source_obj_list, classname=Space.__name__):
    """
    """
    source_list = []
    changed_dict = {}
    for item in source_obj_list:
        source_list.append("{0}/{1}".format(classname, item.id))
        changed_dict[item.id] = item.changed
    return (source_list, changed_dict)


def generate_sitemap_list(sources, changed_dict, source_images=None):
    """
    """
    sitemap_list = []
    processed_url_aliases = []
    url_aliases = UrlAlias.query.filter(UrlAlias.source.in_(sources)).all()
    for item in url_aliases:
        source_id = int(item.source.split('/')[-1])
        record = {
            "loc": "{0}/{1}".format(SITEMAP_DOMAIN, item.alias),
            "priority": DYNAMIC_SITEMAP_PRIORITY,
            "changefreq": DYNAMIC_SITEMAP_FREQUENCY,
            "lastmod": datetime.fromtimestamp(changed_dict[source_id]).strftime("%Y-%m-%d")
        }
        if source_images and source_id in source_images:
            record.update({"images": source_images[source_id]})
        sitemap_list.append(record)
        processed_url_aliases.append(item.pid)
    return (sitemap_list, processed_url_aliases)


def get_image_list(sources):
    """
    """
    source_ids = [int(item.split('/')[-1]) for item in sources]
    fu_list = FileUsage.query.filter(FileUsage.fu_type == "workspaces", FileUsage.type_id.in_(source_ids)).all()
    fid_list = []
    source_fids = {}
    for fu in fu_list:
        source_fids[fu.fid] = fu.type_id
        fid_list.append(fu.fid)
    fm_list = FileManaged.query.filter(FileManaged.fid.in_(fid_list)).all()
    image_sources = {}
    for fm in fm_list:
        uri = fm.uri.split('public:/')[1]
        if not int(source_fids[fm.fid]) in image_sources:
            image_sources[int(source_fids[fm.fid])] = []
        simg_list = image_sources[int(source_fids[fm.fid])]
        simg_list.append("{0}{1}".format(SITEMAP_DOMAIN, uri))
        image_sources[int(source_fids[fm.fid])] = simg_list

    return image_sources


def prettify(elem):
    """Return pretty printed XML string for the element.

    :param elem: Element Tree
    :return: Prettyfied element
    """
    rough_string = tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    style = reparsed.createProcessingInstruction('xml-stylesheet', 'type="text/xsl" href="/sitemap.xsl"')
    urlset = reparsed.firstChild
    reparsed.insertBefore(style, urlset)
    return reparsed.toprettyxml(indent=" ")


def generate_xml(sitemap):
    """Generate xml from sitemap  list

    :param sitemap: Sitemap list containing sitemap information
    :return: Generated xml document
    """
    urlset = Element("urlset")
    urlset.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")
    urlset.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    urlset.set("xmlns:xhtml", "http://www.w3.org/1999/xhtml")
    urlset.set("xmlns:image", "http://www.google.com/schemas/sitemap-image/1.1")
    urlset.set("xsi:schemaLocation", "http://www.sitemaps.org/schemas/sitemap/0.9 "
                                     "http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd")
    for item in sitemap:
        url = SubElement(urlset, "url")
        # Create sub elements for each url
        # loc [url]
        loc = SubElement(url, "loc")
        loc.text = item['loc']
        # change frequency
        changefreq = SubElement(url, "changefreq")
        changefreq.text = item['changefreq']
        # priority
        priority = SubElement(url, "priority")
        priority.text = str(item['priority'])
        # last modified date and time
        lastmod = SubElement(url, "lastmod")
        lastmod.text = str(item['lastmod'])
        if 'images' in item:
            for img_url in item['images']:
                image = SubElement(url, "image:image")
                image_loc = SubElement(image, "image:loc")
                image_loc.text = img_url

    return prettify(urlset)
