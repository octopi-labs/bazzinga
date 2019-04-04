from sqlalchemy import (BigInteger, Column, ForeignKey, ForeignKeyConstraint,
                        Integer, String, PrimaryKeyConstraint)
from sqlalchemy.orm import relationship

from libapp import sqld as db
from libapp.enumerator import SpaceStatus
from libapp.sitemap.models.mixin import IdMixin, ModelMixin, TimestampMixin


class Node(db.Model, TimestampMixin, ModelMixin):
    """
    """
    __tablename__ = "node"
    __table_args__ = {'mysql_row_format': 'DYNAMIC'}

    id = Column("nid", Integer, primary_key=True, autoincrement=True)
    ntype = Column("type", String(255), nullable=False, default="", index=True)


class UrlAlias(db.Model, ModelMixin):
    """
    """
    __tablename__ = "url_alias"
    __table_args__ = {'mysql_row_format': 'DYNAMIC'}

    pid = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    source = Column(String(255), nullable=False, default="", index=True)
    alias = Column(String(255), nullable=False, default="", index=True)


class SpaceCity(db.Model, IdMixin, ModelMixin):
    """
    """
    __tablename__ = "space_city"
    __table_args__ = {'mysql_row_format': 'DYNAMIC'}

    name = Column(String(255), nullable=False, default="", index=True)
    region = Column(String(255), nullable=False, default="", index=True)
    status = Column(Integer, nullable=False, default=0, index=True)


class SpaceCategory(db.Model, IdMixin, ModelMixin):
    """
    """
    __tablename__ = "space_category"
    __table_args__ = {'mysql_row_format': 'DYNAMIC'}

    category = Column(String(255), nullable=False, default="workspace_type", index=True)
    sctype = Column("type", String(255), nullable=False, default="shared", index=True)
    machine_name = Column(String(255), nullable=False, default="desk", index=True)
    label = Column(String(255), nullable=False, default="Desk", index=True)


class Space(db.Model, IdMixin, TimestampMixin, ModelMixin):
    """
    """
    __tablename__ = "space"
    __table_args__ = {'mysql_row_format': 'DYNAMIC'}

    title = Column(String(255), nullable=False, default="", index=True)
    status = Column(Integer, nullable=False, default=SpaceStatus.Incomplete.value)

    workspace_s = relationship("Workspace", back_populates="space_w", cascade="all, delete-orphan")


class Workspace(db.Model, IdMixin, TimestampMixin, ModelMixin):
    """
    """
    __tablename__ = "space_workspaces"
    __table_args__ = {'mysql_row_format': 'DYNAMIC'}

    space_id = Column(Integer, ForeignKey("space.id"))
    name = Column(String(255), nullable=False, default="", index=True)

    space_w = relationship("Space", back_populates="workspace_s", lazy="subquery")


class FileManaged(db.Model, ModelMixin):
    """
    """
    __tablename__ = "file_managed"
    __table_args__ = {'mysql_row_format': 'DYNAMIC', }

    fid = Column(Integer, nullable=False, primary_key=True)
    uid = Column(Integer, nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    uri = Column(String(255), nullable=False, index=True)
    filemime = Column(String(255), nullable=False)
    filesize = Column(BigInteger, nullable=False)
    status = Column(Integer, nullable=False, index=True)
    timestamp = Column(Integer, nullable=False, index=True)
    origname = Column(String(255), nullable=False)
    fm_type = Column("type", String(50), nullable=False, index=True)

    fileusage_fm = relationship("FileUsage", back_populates="filemanaged_fu", cascade="all, delete-orphan")


class FileUsage(db.Model, ModelMixin):
    """
    """
    __tablename__ = "file_usage"
    __table_args__ = {'mysql_row_format': 'DYNAMIC'}
    __table_args__ = (PrimaryKeyConstraint('fid', 'module', 'type', 'id'),)

    fid = Column(Integer, ForeignKey("file_managed.fid"))
    module = Column(String(255), nullable=False, default="")
    fu_type = Column("type", String(255), nullable=False)
    type_id = Column("id", Integer, nullable=False)
    count = Column(Integer, nullable=False)

    filemanaged_fu = relationship("FileManaged", back_populates="fileusage_fm", lazy="subquery")
