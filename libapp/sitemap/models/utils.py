import json
import sys

from flask_sqlalchemy import BaseQuery
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import DeclarativeMeta

from libapp import sqld as db
from libapp.utils import merge_dicts

PY3 = sys.version_info[0] == 3

if PY3:  # pragma: no cover
    string_types = str,  # pragma: no flakes
    text_type = str  # pragma: no flakes
else:  # pragma: no cover
    string_types = basestring,  # pragma: no flakes
    text_type = unicode  # pragma: no flakes


def encode_string(string):
    """Encodes a string to bytes, if it isn't already.

    :param string: String to be encoded
    :return: encoded string
    """
    return string.encode('utf-8') if isinstance(string, text_type) else string


def session_commit():
    """Commit current database session

    :return: reason in case of exception
    """
    try:
        db.session.flush()
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        reason = str(e)
        return reason


def alchemy_json_encoder(revisit_self=False, fields_to_expand=[], fields_to_include=[], fields_to_ignore=[],
                         fields_to_replace={}, fields_to_transform={}):
    """Serialize SQLAlchemy result into JSon

    Inpsired by: http://stackoverflow.com/questions/5022066/how-to-serialize-sqlalchemy-result-to-json
     => A recursive, possibly-circular, selective implementation

    :param revisit_self: True / False
    :param fields_to_expand: Fields which are to be expanded for including their children
    :param fields_to_include: Field to include in the output
    :param fields_to_ignore: Fields to be ignored while encoding
    :param fields_to_replace: Field keys to be replaced by values assigned in dictionary
    :param fields_to_transform: Field to provide keys for which function in values to be used to convert
    :return: Json serialized SQLAlchemy object
    """
    _visited_objs = []

    class AlchemyEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj.__class__, DeclarativeMeta):
                # don't re-visit self
                if revisit_self:
                    if obj in _visited_objs:
                        return None
                    _visited_objs.append(obj)

                # get all the fields to be transformed
                if getattr(obj, "__transform__", None):
                    transformed = merge_dicts(fields_to_transform, getattr(obj, "__transform__")())
                else:
                    transformed = fields_to_transform
                # go through each field in this SqlAlchemy class
                fields = {}
                parent = None
                if hasattr(obj, "__class__") and obj.__class__.__name__.lower() in fields_to_expand:
                    parent = obj.__class__.__name__.lower()
                elif hasattr(obj, "__class__") and obj.__class__.__name__.lower() in fields_to_replace:
                    parent = fields_to_replace[obj.__class__.__name__.lower()]
                else:
                    pass
                field_list = []
                if fields_to_include:
                    field_list += [x for x in dir(obj) if not x.startswith('_') and x != 'metadata' and
                                   (x in fields_to_include or "{0}.{1}".format(parent, x) in fields_to_include)]
                elif fields_to_ignore:
                    field_list += [x for x in dir(obj) if not x.startswith('_') and x != 'metadata' and
                                   not (x in fields_to_ignore or "{0}.{1}".format(parent, x) in fields_to_ignore)]
                else:
                    pass
                if getattr(obj, "__response__", None):
                    field_list += getattr(obj, "__response__")()
                if fields_to_expand:
                    field_list += [x for x in dir(obj) if not x.startswith('_') and x != 'metadata' and
                                   (x in fields_to_expand or "{0}.{1}".format(parent, x) in fields_to_expand)]
                field_list = list(set(field_list).difference(fields_to_ignore))
                for field in field_list:
                    val = obj.__getattribute__(field)
                    # is this field method definition, or an SQLAlchemy object
                    if not hasattr(val, "__call__") and not isinstance(val, BaseQuery):
                        field_name = fields_to_replace[field] if field in fields_to_replace else field
                        # is this field another SQLAlchemy object, or a list of SQLAlchemy objects?
                        if isinstance(val.__class__, DeclarativeMeta) or \
                                (isinstance(val, list) and len(val) > 0 and isinstance(val[0].__class__,
                                                                                       DeclarativeMeta)):

                            # unless we're expanding this field, stop here
                            if field not in fields_to_expand:
                                # not expanding this field: set it to None and continue
                                # fields[field_name] = None
                                continue
                        if val is not None:
                            fields[field_name] = (encode_string(val) if field_name not in transformed
                                                  else transformed[field_name](val))
                        else:
                            fields[field_name] = None
                # a json-encodable dict
                return fields if len(fields) > 1 else fields[fields.keys()[0]]

            return json.JSONEncoder.default(self, obj)
    return AlchemyEncoder
