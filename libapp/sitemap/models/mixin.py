import gc
import traceback
from datetime import datetime

from sqlalchemy import Column, Enum, Integer

from libapp import app
from libapp import sqld as db
from libapp.exceptions import DataException
from libapp.sitemap.models.utils import session_commit


class IdMixin(object):
    """Mixin class to add id to the model object
    """
    id = Column(Integer, primary_key=True, autoincrement=True)


class TimestampMixin(object):
    """Mixin class to add created and updated timestamps to the model object
    """
    created = Column(Integer, nullable=False, default=0)
    changed = Column(Integer, nullable=False, default=0, onupdate=datetime.utcnow().strftime('%s'))


class ModelMixin(object):
    """Mixin class to add delete and update functions
    """
    @staticmethod
    def __assign_field_values(obj, **kwargs):
        """Assign key value pairs as fields of the model object

        :param obj: Model object for which to assign key value pairs
        :param kwargs: Dictionary of key value pairs
        :return: Object with fields assigned with values
        """
        for key, value in kwargs.iteritems():
            if value is not None:
                setattr(obj, key, value)
        return obj

    def delete(self):
        """Delete model object

        :return: Deleted model object
        """
        db.session.delete(self)
        error = session_commit()
        if error:
            raise DataException(message=error, errorcode=404)
        return self

    def update(self, **kwargs):
        """Update model object

        :param kwargs: Dictionary containing fields to be updated
        :return: Updated model object
        """
        self = ModelMixin.__assign_field_values(self, **kwargs)
        db.session.add(self)
        error = session_commit()
        if error:
            raise DataException(message=error, errorcode=404)
        return self

    @classmethod
    def add(cls, **kwargs):
        """Add new model object

        :param kwargs: Dictionary containing fields to be assigned to object
        :return: added model object
        """
        obj = ModelMixin.__assign_field_values(cls(), **kwargs)
        obj.created = obj.updated = datetime.utcnow().strftime('%s')
        db.session.add(obj)
        error = session_commit()
        if error:
            raise DataException(message=error, errorcode=404)
        if not obj.id:
            raise DataException(message="Could not add {}".format(obj.__class__.__name__), errorcode=403)
        return obj

    @classmethod
    def assign(cls, **kwargs):
        """Assign mapping table values or files to model object

        :param kwargs: Dictionary containing references to objects and file objects
        :return: files assigned object
        """
        obj = ModelMixin.__assign_field_values(cls(), **kwargs)
        db.session.add(obj)
        error = session_commit()
        if error:
            raise DataException(message=error, errorcode=404)
        return obj

    @classmethod
    def save_bulk(cls, object_list):
        """ Save all the objects present in object list

        :param object_list: List of objects
        :return: True if successful
        """
        if object_list:
            try:
                db.session.bulk_save_objects(object_list)
            except Exception as e:
                app.logger.exception(traceback.print_stack())
                db.session.rollback()
                return False
            error = session_commit()
            if error:
                raise DataException(message=error, errorcode=403)
        return True

    @classmethod
    def save_n_clear_list(cls, object_list):
        """Add / Update database with values from list provided and clear list
            This will also collect garbage if needed

        :param object_list:List of objects to be added / updated
        :return: clean list
        """
        cls.save_bulk(object_list)
        del object_list[:]
        gc.collect()
        return object_list
