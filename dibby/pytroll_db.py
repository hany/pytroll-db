#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2010-2015.

# Author(s):

#   Esben S. Nielsen   <esn@dmi.dk>
#   Kristian R. Larsen <krl@dmi.dk>
#   Adam Dybbroe       <adam.dybbroe@smhi.se>

# This file is part of pytroll.

# Pytroll is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.

# Pytroll is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with
# pytroll.  If not, see <http://www.gnu.org/licenses/>.

import datetime

# from sqlalchemy import Column, Integer, String, Boolean, DateTime,\
#                       create_engine, ForeignKey, Table
from sqlalchemy import Integer, String, Boolean, DateTime,\
    create_engine, ForeignKey, Table, Column

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relation, sessionmaker

# from geoalchemy.postgis import PGComparator
from geoalchemy2 import Geometry, Geography
from geoalchemy2.shape import from_shape
# from geoalchemy import (GeometryColumn, Point, Polygon, LineString,
#        GeometryDDL, WKTSpatialElement, DBSpatialElement, GeometryExtensionColumn,
#        WKBSpatialElement)

# from osgeo import ogr

# from sqltypes import LINESTRING, POLYGON

Base = declarative_base()

# relation table
data_boundary = Table('data_boundary', Base.metadata,
                      Column('uid', String,
                             ForeignKey('file.uid', ondelete="CASCADE")),
                      Column('boundary_id', Integer,
                             ForeignKey('boundary.boundary_id')))

# relation table
file_type_parameter = Table('file_type_parameter', Base.metadata,
                            Column('file_type_id', Integer,
                                   ForeignKey('file_type.file_type_id')),
                            Column('parameter_id', Integer,
                                   ForeignKey('parameter.parameter_id')))

# relation table
file_tag = Table('file_tag', Base.metadata,
                 Column('tag_id', Integer,
                        ForeignKey('tag.tag_id')),
                 Column('uid', String,
                        ForeignKey('file.uid', ondelete="CASCADE")))

# relation table
file_type_tag = Table('file_type_tag', Base.metadata,
                      Column('tag_id', Integer,
                             ForeignKey('tag.tag_id')),
                      Column('file_type_id', Integer,
                             ForeignKey('file_type.file_type_id')))


class ParameterType(Base):

    """Mapping the DB-table parameter_type to a python object
    """
    __tablename__ = 'parameter_type'

    # mapping
    parameter_type_id = Column(Integer, primary_key=True)
    parameter_type_name = Column(String)
    parameter_location = Column(String)

    def __init__(self, parameter_type_id, parameter_type_name, parameter_location):
        self.parameter_type_id = parameter_type_id
        self.parameter_type_name = parameter_type_name
        self.parameter_location = parameter_location


class Parameter(Base):
    __tablename__ = 'parameter'

    # mapping
    parameter_id = Column(Integer, primary_key=True)
    parameter_type_id = Column(
        Integer, ForeignKey('parameter_type.parameter_type_id'))
    parameter_name = Column(String)
    description = Column(String)

    def __init__(self, parameter_id, parameter_type_id, parameter_name, description):
        self.parameter_id = parameter_id
        self.parameter_type_id = parameter_type_id
        self.parameter_name = parameter_name
        self.description = description


class Tag(Base):
    __tablename__ = 'tag'

    # mapping
    tag_id = Column(Integer, primary_key=True)
    tag = Column(String)

    def __init__(self, tag_id, tag):
        self.tag_id = tag_id
        self.tag = tag


class FileFormat(Base):
    __tablename__ = 'file_format'

    # mapping
    file_format_id = Column(Integer, primary_key=True)
    file_format_name = Column(String)
    description = Column(String)

    def __init__(self, file_format_id, file_format_name, description):
        self.file_format_id = file_format_id
        self.file_format_name = file_format_name
        self.description = description


class FileType(Base):
    __tablename__ = 'file_type'

    # mapping
    file_type_id = Column(Integer, primary_key=True)
    file_type_name = Column(String)
    description = Column(String)

    def __init__(self, file_type_id, file_type_name, description):
        self.file_type_id = file_type_id
        self.file_type_name = file_type_name
        self.description = description


class File(Base):
    __tablename__ = 'file'

    # mapping
    uid = Column(String, primary_key=True)
    file_type_id = Column(Integer, ForeignKey('file_type.file_type_id'))
    file_format_id = Column(Integer, ForeignKey('file_format.file_format_id'))
    is_archived = Column(Boolean)
    creation_time = Column(DateTime)

    def __init__(self, uid, file_type, file_format, is_archived, creation_time):
        self.uid = uid
        self.file_type = file_type
        self.file_format = file_format
        self.is_archived = is_archived
        self.creation_time = creation_time


class Boundary(Base):
    __tablename__ = 'boundary'

    # mapping
    boundary_id = Column(Integer, primary_key=True)
    boundary_name = Column(String)
    boundary = Column(Geometry('POLYGON'))
    creation_time = Column(DateTime)

    def __init__(self, boundary_id, boundary_name, boundary, creation_time=None):
        self.boundary_id = boundary_id
        self.boundary_name = boundary_name
        self.boundary = boundary
        if creation_time is None:
            creation_time = datetime.datetime.utcnow()
        self.creation_time = creation_time


class ParameterLinestring(Base):
    __tablename__ = 'parameter_linestring'

    # mapping
    uid = Column(
        String, ForeignKey('file.uid', ondelete="CASCADE"), primary_key=True)
    parameter_id = Column(
        Integer, ForeignKey('parameter.parameter_id'), primary_key=True)
    creation_time = Column(DateTime)
    data_value = Column(Geography('LINESTRING'))
    # data_value = GeometryColumn(LineString(2))

    def __init__(self, file_obj, parameter, data_value, creation_time):
        self.file_obj = file_obj
        self.parameter = parameter
        self.creation_time = creation_time
        self.data_value = data_value


class ParameterValue(Base):
    __tablename__ = "parameter_value"

    # mapping
    uid = Column(
        String, ForeignKey('file.uid', ondelete="CASCADE"), primary_key=True)
    parameter_id = Column(
        Integer, ForeignKey('parameter.parameter_id'), primary_key=True)
    data_value = Column(String)
    creation_time = Column(DateTime)

    def __init__(self, file_obj, parameter, data_value, creation_time):
        self.file_obj = file_obj
        self.parameter = parameter
        self.creation_time = creation_time
        self.data_value = data_value


class FileAccessURI(Base):
    __tablename__ = "file_access_uri"

    # mapping
    file_type_id = Column(
        Integer, ForeignKey('file_type.file_type_id'), primary_key=True)
    file_format_id = Column(
        Integer, ForeignKey('file_format.file_format_id'), primary_key=True)
    sequence = Column(Integer, primary_key=True)
    uri = Column(String, primary_key=True)

    def __init__(self, file_type, file_format, sequence, uri):
        self.file_type = file_type
        self.file_format = file_format
        self.sequence = sequence
        self.uri = uri


class FileURI(Base):
    __tablename__ = "file_uri"

    # mapping
    uid = Column(String,
                 ForeignKey('file.uid', ondelete="CASCADE"),
                 primary_key=True)
    uri = Column(String, primary_key=True)

    def __init__(self, uid, uri):
        self.uid = uid
        self.uri = uri


class SpatialRefSys(Base):
    __tablename__ = "spatial_ref_sys"

    # mapping
    srid = Column(Integer, primary_key=True)
    auth_name = Column(String)
    auth_srid = Column(Integer)
    srtext = Column(String)
    proj4text = Column(String)  # character varying(2048),
    # CONSTRAINT spatial_ref_sys_pkey PRIMARY KEY (srid),
    # CONSTRAINT spatial_ref_sys_srid_check CHECK (srid > 0 AND srid <= 998999)


# GeometryDDL(ParameterLinestring.__table__)

#
# Relations

# ParameterType
ParameterType.parameters = relation(Parameter, backref='parameter_type')

# Parameter
Parameter.parameter_values = relation(ParameterValue, backref='parameter')
Parameter.parameter_linestrings = relation(
    ParameterLinestring, backref='parameter')

# FileFormat
FileFormat.file_uris = relation(FileAccessURI, backref='file_format')
FileFormat.file_objs = relation(File, backref='file_format')

# FileType
FileType.parameters = relation(
    Parameter, secondary=file_type_parameter, backref='file_types')
FileType.file_uris = relation(FileAccessURI, backref='file_type')
FileType.file_objs = relation(File, backref='file_type')
FileType.file_type_tags = relation(
    Tag, secondary=file_type_tag, backref='file_types')


# File
File.parameter_values = relation(
    ParameterValue, backref='file_obj', cascade="all, delete, delete-orphan")
File.parameter_linestrings = relation(
    ParameterLinestring, backref='file_obj', cascade="all, delete, delete-orphan")
File.file_tags = relation(
    Tag, secondary=file_tag, backref='file_objs', cascade="all, delete")
File.boundary = relation(
    Boundary, secondary=data_boundary, backref='file_objs', cascade="all, delete")

# FileURI
FileURI.file_obj = relation(File, backref='uris')


class DCManager(object):

    """Data Center Manager
    """

    def __init__(self, connection_string):
        engine = create_engine(connection_string)
        self._engine = engine
        Session = sessionmaker(bind=engine)
        self._session = Session()

    @property
    def engine(self):
        return self._engine

    @property
    def session(self):
        return self._session

    def save(self):
        try:
            self._session.commit()
        except Exception:
            self._session.rollback()
            raise

    def rollback(self):
        self._session.rollback()

    def create_file_type(self, file_type_id, file_type_name, description):
        file_type = FileType(file_type_id, file_type_name, description)
        self._session.add(file_type)
        return file_type

    def create_file_format(self, file_format_id, file_format_name, description):
        file_format = FileFormat(file_format_id, file_format_name, description)
        self._session.add(file_format)
        return file_format

    def create_file_uri(self, uid, URI):
        file_uri = FileURI(uid, URI)
        self._session.add(file_uri)
        return file_uri

    def create_parameter_type(self, parameter_type_id, parameter_type_name, parameter_location):
        parameter_type = ParameterType(
            parameter_type_id, parameter_type_name, parameter_location)
        self._session.add(parameter_type)
        return parameter_type

    def create_parameter(self, parameter_id, parameter_type, parameter_name, description):
        parameter = Parameter(
            parameter_id, parameter_type, parameter_name, description)
        self._session.add(parameter)
        return parameter

    def create_file_type_parameter(self, file_type=None,
                                   file_type_name=None,
                                   parameters=None,
                                   parameter_names=None):
        """ Creates a relation between a filetype and a parameter

            Parameters :
                file_type : FileType object
                file_type_name : str
                        FileType object name
                parameters : list
                        list of Parameter objects
                parameter_names : list
                        list of Parameter object names

            Returns:
                FileType object with new relations

        Notice :
            Either file_type or file_type_name must be provided
            Either parameters or parameter_names must be provided
        """

        if not file_type:
            if file_type_name:
                file_type = self.get_file_type(file_type_name)
            else:
                raise TypeError("No FileType reference defined")

        if parameters:
            for param in parameters:
                file_type.parameters.append(param)
        elif parameter_names:
            for parameter_name in parameter_names:
                parameter = self.get_parameter(parameter_name)
                file_type.parameters.append(parameter)
        else:
            raise TypeError("No FileType reference defined")

        return file_type

    def create_parameter_value(self, data_value,
                               file_obj=None,
                               uid=None,
                               parameter=None,
                               parameter_name=None,
                               creation_time=None):
        """Creates a ParameterValue object from a data value and File and
        Parameter references.

            Parameters :
                data_value :
                    data value corresponding to parameter type
                file_obj : File object
                uid : str
                    File object name
                parameter : Parameter object
                parameter_name : str
                    Parameter name
                creation_time : datetime object
                    Time of creation

                Returns : 
                    ParameterValue Object

        Notice : 
            Either file_obj or uid must be provided
            Either parameter or parameter_name must be provided

        """

        if not creation_time:
            creation_time = datetime.datetime.utcnow()

        if not file_obj:
            if uid:
                file_obj = self.get_file(uid)
            else:
                raise TypeError("No file reference defined")

        if not parameter:
            if parameter_name:
                parameter = self.get_parameter(parameter_name)
            else:
                raise TypeError("No parameter reference defined")

        parameter_value = ParameterValue(
            file_obj, parameter, data_value, creation_time)
        self._session.add(parameter_value)
        return parameter_value

    def create_parameter_linestring(self, linestring,
                                    file_obj=None,
                                    uid=None,
                                    parameter=None,
                                    parameter_name=None,
                                    creation_time=None):
        """Creates a ParameterLinestring object from a linestring and File and
        Parameter references.

            Parameters:
                linestring : shapely linestring object
                file_obj : File object
                uid : str
                    File object name
                parameter : Parameter object
                parameter_name : str
                    Parameter name
                creation_time : datetime object
                    Time of creation

                Returns : 
                    ParameterLinestring Object

        Notice : 
            Either file_obj or uid must be provided
            Either parameter or parameter_name must be provided

        """

        if not creation_time:
            creation_time = datetime.datetime.utcnow()

        if not file_obj:
            if uid:
                file_obj = self.get_file(uid)
            else:
                raise TypeError("No file reference defined")

        if not parameter:
            if parameter_name:
                parameter = self.get_parameter(parameter_name)
            else:
                raise TypeError("No parameter reference defined")

        parameter_linestring = ParameterLinestring(
            file_obj, parameter, from_shape(linestring), creation_time)
        self._session.add(parameter_linestring)
        return parameter_linestring

    def create_boundary(self, boundary_id, boundary_name, boundary, creation_time=None):
        if creation_time is None:
            creation_time = datetime.datetime.utcnow()
        boundary_obj = Boundary(
            boundary_id, boundary_name, boundary, creation_time)
        self._session.add(boundary_obj)
        return boundary_obj

    def create_tag(self, tag_id, tag):
        tag_obj = Tag(tag_id, tag)
        self._session.add(tag_obj)
        return tag_obj

    def get_file_type(self, file_type_name):
        return self._session.query(FileType).\
            filter(FileType.file_type_name == file_type_name).one()

    def get_file_format(self, file_format_name):
        return self._session.query(FileFormat).\
            filter(FileFormat.file_format_name == file_format_name).one()

    def get_parameter(self, parameter_name):
        return self._session.query(Parameter).\
            filter(Parameter.parameter_name == parameter_name).one()

    def get_file(self, uid):
        return self._session.query(File).\
            filter(File.uid == uid).one()

    def get_files(self, file_type_name=None, oldest_creation_time=None,
                  newest_creation_time=None):
        if newest_creation_time is None:
            newest_creation_time = datetime.datetime.utcnow()
        if oldest_creation_time is None:
            oldest_creation_time = datetime.datetime(1, 1, 1)

        if file_type_name is None:
            return self._session.query(File).\
                filter(File.creation_time > oldest_creation_time).\
                filter(File.creation_time < newest_creation_time).all()

        return self._session.query(File).\
            filter(FileType.file_type_name == file_type_name).\
            filter(File.file_type_id == FileType.file_type_id).\
            filter(File.creation_time > oldest_creation_time).\
            filter(File.creation_time < newest_creation_time).all()

    def get_within_area_of_interest(self, boundingbox, file_type_name=None, distance=0):
        """Get all files within *distance* of area of interest.
        E.g.: boundingbox = [(1.7, 54.8), (28.7, 54.9), (34.8, 71.2), (2.3, 71.7)]'
        distance in km.
        """

        # retv = self._session.query(ParameterLinestring).\
        #    filter(ParameterLinestring.data_value.intersects(boundingbox)).count()
        # retv = self._session.query(ParameterLinestring).\
        #    filter(ParameterLinestring.data_value.intersects(boundingbox) == True).all()
        # retv = self._session.query(ParameterLinestring).\
        #    filter(ParameterLinestring.data_value.distance(boundingbox)/1000. <= 0.).all()
        # retv = self._session.query(File).from_statement(
        #    "select f.* from file f, parameter_linestring pl where ST_Distance(ST_GeomFromText(:bbox), pl.data_value) < 1000000.").\
        #             params(bbox=boundingbox).all()
        # retv = self._session.query(File).from_statement(
        #    "select f.* from file f, parameter_linestring pl where ST_Distance(pl.data_value, ST_GeomFromText(:bbox)) < 1.").\
        #    params(bbox=boundingbox).all()
        # retv = self._session.query(File).from_statement(
        #    "select * from (select uid, ST_Distance(data_value, 'POLYGON ((1.7  54.8, 28.7 54.9, 34.8 71.2, 2.3 71.7, 1.7  54.8))':: geography)/1000. as dist from parameter_linestring) dlist where dlist.dist < 1000").all()

        polypoints = boundingbox + [boundingbox[0]]

        poly = "POLYGON ((" + ", ".join(str(item[0]) + " " + str(item[1])
                                        for item in polypoints) + "))"

        retv = self._session.query(File).from_statement(
            "select * from (select uid, ST_Distance(data_value, '" +
            poly + "':: geography)/1000. as dist from parameter_linestring) " +
            "dlist where dlist.dist <= " + str(distance)).all()

        return retv

# select * from
#(
# select uid, ST_Distance(data_value, 'POLYGON ((1.7  54.8, 28.7 54.9, 34.8 71.2, 2.3 71.#7, 1.7  54.8))':: geography)/1000. as dist from parameter_linestring
#) dlist where dlist.dist < 1000

        # return self._session.query(File).\
        #    filter(File.file_type_id == FileType.file_type_id).\
# select * from
#(
# select uid, ST_Distance(data_value, 'POLYGON ((1.7  54.8, 28.7 54.9, 34.8 71.2, 2.3 71.7, 1.7  54.8))':: ge#ography)/1000. as dist from parameter_linestring
#) dlist where dlist.dist < 1000

    def create_file(self, uid,
                    is_archived=False,
                    creation_time=datetime.datetime.utcnow(),
                    file_type=None,
                    file_type_id=None,
                    file_type_name=None,
                    file_format=None,
                    file_format_id=None,
                    file_format_name=None):
        """Creates a File object from a file name and FileType and
        FileFormat references.

            Parameters:
                file_type : FileType object
                file_type_id : int
                    FileType object id
                file_type_name : str
                    FileType object name
                file_format : FileFormat object
                file_format_id : int
                    FileFormat object id
                file_format_name : str
                    FileFormat object name
                creation_time : datetime object
                    Time of creation
                is_archived : boolean
                    if file is archived

                Returns : 
                    File Object

        Notice : 
            Either file_type or file_type_id or file_type_name must be provided
            Either file_format or file_format_id or file_format_name must be provided

        """

        if not file_type:
            if file_type_id:
                file_type = self._session.query(FileType).\
                    filter(FileType.file_type_id == file_type_id).one()
            elif file_type_name:
                file_type = self.get_file_type(file_type_name)
            else:
                raise TypeError("file_type not defined")

        if not file_format:
            if file_format_id:
                file_format = self._session.query(FileType).\
                    filter(FileFormat.file_format_id == file_format_id).one()
            elif file_format_name:
                file_format = self.get_file_format(file_format_name)
            else:
                raise TypeError("file_format not defined")

        file_obj = File(
            uid, file_type, file_format, is_archived, creation_time)

        self._session.add(file_obj)
        return file_obj

    def delete(self, sqla_object):
        self._session.delete(sqla_object)

if __name__ == '__main__':
    # rm = DCManager('postgresql://iceopr@devsat-lucid:5432/testdb2')
    # rm = DCManager('postgresql://a000680:@localhost.localdomain:5432/sat_db')

    dcm = DCManager('postgresql://polar:polar@safe:5432/sat_db')
    boundingbox = 'POLYGON ((1.7  54.8, 28.7 54.9, 34.8 71.2, 2.3 71.7, 1.7  54.8))'

    res = dcm.get_within_area_of_interest(boundingbox)
    print res[0].uid

    # f = rm.get_file()
    # pl = f.parameter_linestrings[0]
    # print type(pl.data_value)
    # print pl.data_value.wkt
