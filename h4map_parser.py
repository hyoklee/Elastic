#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
###########################################################################
# Copyright (C) 2015 The HDF Group
#
# Author: Hyo-Kyung Lee (hyoklee@hdfgroup.org)
#
# Last Update: 2015/12/30
###########################################################################
"""
   This module parses an HDF4 content map file and loads the contents of file
   as S3 binary object and produces Elastic-indexable JSON document.
"""

from pyes import *
import lxml.etree as etree
import os
import unittest
import hashlib
import json
from optparse import OptionParser

conn = ES('127.0.0.1:9200')
# conn.indices.create_index("osdc-8a052845")

class H4MapParser(object):

    """H4Map parser class"""

    def __init__(self, xml_file):
        """
        Constructor.
        @param xml_file: HDF4 file content map XML file
        """
        self.xml_file = xml_file
        self.depth = 0
        self.tree = None
        self.last = "group"
        self.meta_core = None
        self.meta_struct = None
        self.meta_prod = None
        self.meta_arch = None
        self.file_name = None
        self.file_desc = []
        self.group_stack = []
        self.parents = None
        try:
            self.tree = etree.parse(self.xml_file).getroot()
        except etree.XMLSyntaxError as err:
            print 'ERROR:The HDF4 map file is not valid:' + xml_file
            print err
            return None
        except IOError as err:
            print 'ERROR:Can\'t read the HDF4 map file :' + self.xml_file
            print err
            return None

        self.schema = "{http://www.hdfgroup.org/HDF4/XML/schema/HDF4map/1.0.1}"
        tag = self.schema + "HDF4FileInformation"
        item = self.tree.find(tag)
        if item is not None:
            file_node_info = item.getchildren()
            self.file_name = file_node_info[0].text
            flv_node = file_node_info[1].find(self.schema+"fileLocationValue")
            self.file_path = flv_node.text
            print self.file_path
        else:
            print 'ERROR:Can\'t read HDF4FileInformation from HDF4 map file.'
            return None

        self.dims = {}
        self.dimscales = {}
                
    def parse_content(self, conv=[], test=False):
        """
        Parses the XML.
        """
        # print "Processing : " + self.xml_file
        self.depth = 1
        self.group_stack.append('/')
        self.recursive_walk(self.tree, self.depth)
 

    def parse_dimension(self, node, dim_list, dset):
        """
        Parses dimensionRef and attaches dimension scales. 
        """
        for items in node.getiterator(tag=self.schema + "dimensionRef"):
            # Create a map of dimension name and size.
            index = int(items.attrib["dimensionIndex"])
            size = int(dim_list[index])
            # Create dimension scale if it has not been created.
            name = items.attrib["name"]
            if name == '':
                print 'WARNING:dimension name is empty - will use ref.'
                name = items.attrib["ref"]
            if name not in self.dims.keys():
                self.dims[name] = size
            else:
                t_dim = self.dimscales[name]
            #self.hpd.attach_dimension(t_dim, dset, index)                

    def recursive_walk(self, root_node, depth):
        """
        This recursive function traverse the XML document using the
        ElementTree API; all the nodess are stored in a tree-like structure.
        @param root_node: lxml root node of the map file
        @param depth: used to keep track of the recursion level, 0 on the root.
        """
        # print 'recursiv_walk():'
        # print 'stack length='+str(len(self.group_stack))
        # print 'd='+str(depth)+' self.d='+str(self.depth)+'
        # self.last='+self.last
        self.depth = depth
        for node in root_node.getchildren():
            # print node
            last = None
            # Attribute
            if (node.tag == (self.schema + "FileAttribute") or
                    node.tag == (self.schema + "ArrayAttribute") or
                    node.tag == (self.schema + "GroupAttribute")):
                # print  "-" *self.depth + "attribute: " + node.attrib["name"]

                

                datum_node = node.find(self.schema + "datum")
                value = ""
                if datum_node.attrib["dataType"] == "char8":
                    value_node = node.find(self.schema + "stringValue")
                    value = value_node.text
                    h5type = 'string'
                else:
                    value_node = node.find(self.schema + "numericValues")
                    value = self.get_value_str(value_node.text)
                    h5type = datum_node.attrib["dataType"]

                if node.attrib["name"] == "File Description":
                    self.file_desc.append(value)
                else:
                    if not value:
                        msg = ''.join(['WARNING: Attribute "',
                                       node.attrib["name"],
                                       '" has no value.'
                                       ])
                        print msg
                        value = '\0'

                last = 'attribute'
                # Save metadata for ODL parsing at the end.
                if node.attrib["name"] == "coremetadata":
                    self.meta_core = value
                if node.attrib["name"] == "CoreMetadata.0":
                    self.meta_core = value
                if node.attrib["name"] == "productmetadata":
                    self.meta_prod = value
                if node.attrib["name"] == "archivemetadata":
                    self.meta_arch = value
                if node.attrib["name"] == "ArchiveMetadata.0":
                    self.meta_arch = value
                if node.attrib["name"] == "StructMetadata.0":
                    self.meta_struct = value
                # This is only useful for OSDC EO-1 HDF Level 0 data.
                if node.attrib['name'] == 'Time of L0 File Generation (UTC)':
                    self.datetime = value[:-2]
            # Group
            if node.tag == (self.schema + "Group"):
                i = len(self.group_stack) + 1 - self.depth
                if self.last != "group" or i > 0:
                    while i > 0:
                        self.group_stack.pop()
                        i = i - 1
                    item = self.group_stack[-1]
                self.group_stack.append(node.attrib["name"])
                last = "group"

            # Variable
            if node.tag == (self.schema + "Array"):
                # print  "-" *self.depth+"variable: "+node.attrib["name"]
                # Select the right group in the tree.
                if self.last != "group":
                    item = self.group_stack[-1]
                datum_node = node.find(self.schema + "datum")
                arrayData_node = node.find(self.schema + "arrayData")
                dimsize_node = node.find(self.schema + "dataDimensionSizes")
                str_shape = ''
                # print node.attrib["name"]
                if dimsize_node is not None:
                    dim_list = dimsize_node.text.split(' ')
                    for dim in dim_list:
                        str_shape = str_shape + str(dim) + ','
                    str_shape = str_shape[:-1]
                    self.dtype = datum_node.attrib["dataType"]
                    prop = self.parse_arrayData(node, str_shape)
                    # Attach dimension to the dataset.
                    # self.parse_dimension(node, dim_list, item)
                last = "variable"

            # Dimension
            if node.tag == (self.schema + "Dimension"):
                if self.last != "group":
                    item = self.group_stack[-1]
                    #self.hpd.tree.SelectItem(item, True)

                # print  "-" *self.depth + "dimension: " + node.attrib["name"]
                name = node.attrib["name"]
                # #self.hpd.create_dimension(name, str(self.dims[name]), False)
                last = "dimension"

            if node.tag == (self.schema + "Table"):
                print 'INFO:Skipping unsupported Table ' + node.attrib["name"]
                if self.last != "group":
                    item = self.group_stack[-1]
                    #self.hpd.tree.SelectItem(item, True)
                last = "table"

            if not last:
                last = "unknown"

            self.last = last
            if len(node) > 0:
                self.recursive_walk(node, self.depth + 1)
                self.depth = self.depth - 1

    def parse_chunks(self, node, prop):
        """Parse chunk dimension size if chunks are defined."""
        prop['layout'] = 0
        chunks_node = node.find(self.schema + "chunks")
        if chunks_node is not None:
            chunkDimensionSizes_node = chunks_node.find(
                self.schema + "chunkDimensionSizes")
            if chunkDimensionSizes_node is not None:
                prop['layout'] = 1
                str_shape = ''
                dim_list = chunkDimensionSizes_node.text.split(' ')
                for dim in dim_list:
                    str_shape = str_shape + str(dim) + ','
                str_shape = str_shape[:-1]
                prop['chunk'] = str_shape
            for c_node in chunks_node.getchildren():
                if (c_node.tag == (self.schema + "byteStream")):
                    self.parse_byteStream(c_node, prop, c_node.attrib['chunkPositionInArray'])
        else:
            for bnode in arrayData_node.getchildren():
                if (bnode.tag == (self.schema + "byteStream")):
                    self.parse_byteStream(bnode, prop)
                elif (bnode.tag == (self.schema + "byteStreamSet")):
                    for b_node in bnode.getchildren():
                        self.parse_byteStream(b_node, prop)


    def parse_byteStream(self, bnode, prop, chunk_p=None):
        """Parse byteStream tag.
        """
        if (bnode.tag == (self.schema + "byteStream")):
            self.offset = int(bnode.attrib['offset'])
            self.nBytes = int(bnode.attrib['nBytes'])
            self.file_handler=file(self.file_path+'/'+self.file_name,"rb")            
            self.file_handler.seek(self.offset)
            buf = self.file_handler.read(self.nBytes)
            hash = hashlib.md5()
            hash.update(buf)
            self.md5 =  hash.hexdigest()

            # To-do: Support direct S3 writing.
            # You can store data as numpy object, too.
            # with open(self.md5+'.bin', 'wb') as bfile:
            #    bfile.write(buf)

            # To-do: Call Elastic API directly later with PyES.

            prop['filename'] = self.file_name
            prop['type'] = self.dtype
            # prop['datetime'] = self.datetime
            prop['offset'] = self.offset
            prop['length'] = self.nBytes
            prop['md5'] = self.md5
            if chunk_p:
                prop['chunk_position'] = chunk_p

            conn.index(prop, 'osdc-8a052845', self.dtype)
            # with open(self.md5+'.json', 'w') as outfile:
            #    json.dump(prop, outfile)

    def parse_arrayData(self, node, str_shape):
        """Parse dataset creation properties."""
        prop = {}
        filtr = None
        level = None
        prop['name'] = node.attrib['name']        
        prop['shape'] = str_shape
        arrayData_node = node.find(self.schema + "arrayData")
        if arrayData_node is not None:
            self.parse_chunks(arrayData_node, prop)
            if 'compressionType' in arrayData_node.attrib.keys():
                filtr = arrayData_node.attrib["compressionType"]
            if 'deflate_level' in arrayData_node.attrib.keys():                
                level = arrayData_node.attrib["deflate_level"]
        else:
            prop['layout'] = 0

        if filtr == 'deflate':
            if not level:
                print 'ERROR:no level is specified for gzip compression'
            else:
                prop['gz'] = int(level)
            if prop['layout'] == 0:
                # print 'Setting default chunk layout for HDF5 filter.'
                prop['layout'] = 1
                prop['chunk'] = str_shape
                
            return prop
        else:
            if filtr:
                print 'WARNING:unsupported filter:'+filtr
                return None
            else:
                return prop
        



    def parse_metadata(self):
        """Parse metadata into group structure."""
        if self.meta_struct:
            #self.hpd.tree.SelectItem(#self.hpd.root, True)
            d_struct = parse_odl(self.meta_struct)
            if d_struct is not None:
                self.add_metadata(di_meta=d_struct)
            else:
                print 'ERROR:ODL parsing failed for StructMetadata.'
        if self.meta_core:
            #self.hpd.tree.SelectItem(#self.hpd.root, True)
            d_core = parse_odl(self.meta_core)
            if d_core is not None:
                self.add_metadata(di_meta=d_core)
            else:
                print 'ERROR:ODL parsing failed for CoreMetadata.'

        if self.meta_prod:
            d_prod = parse_odl(self.meta_prod)
            if d_prod is not None:
                self.add_metadata(di_meta=d_prod)
            else:
                print 'ERROR:ODL parsing failed for ProductMetadata.'
        if self.meta_arch:
            d_arch = parse_odl(self.meta_arch)
            if d_arch is not None:
                self.add_metadata(di_meta=d_arch)
            else:
                print 'ERROR:ODL parsing failed for ArchiveMetadata.'

        if len(self.file_desc) > 0:
            self.add_attr_file_desc('File_Description', self.file_desc)

    def add_group(self, parent, k):
        """Add metadta group."""
        #self.hpd.tree.SelectItem(self.parents[parent])
        return #self.hpd.create_group(k, False)

    def add_attr(self, parent, k, val):
        """Add metadta attribute."""
        if isinstance(val, str):
            return
        elif isinstance(val, int):
            return
        elif isinstance(val, float):
            return
        elif isinstance(val, list):
            if all(isinstance(x, int) for x in val):
                return
            if any(isinstance(x, float) for x in val):
                return
            if all(isinstance(x, str) for x in val):
                _value = ','.join(val)
                return
            print 'WARNING:List has a mix of types:' + 'attr=' + k + ' val=' + str(val)
        else:
            print 'WARNING:Unknown instance for attribute:' + k


    def get_value_str(self, value):
        """Format value. h4map value can be separated by space. """
        str_value = ''
        if value == "":
            print 'WARNING:Value is empty.'
            str_value = ''
        else:
            if len(value.split()) > 1:
                for val in value.split():
                    str_value = str_value + str(val) + ','
                str_value = str_value[:-1]
                str_value = '[' + str_value + ']'
            else:
                str_value = value
        return str_value


class TestH4MapParser(unittest.TestCase):

    """Unit test class."""

    def setUp(self):
        """Initialize class."""
        self.parser = H4MapParser('EO12004074_658A6589_r1_HGS_01.L0.xml')

    def test_parser(self):
        """Test parser. """
        self.parser.parse_content()


if __name__ == '__main__':
    # unittest.main()
    parser = OptionParser()
    parser.add_option("-f", "--file", dest="filename",type="string", 
                  help="Loads the XML FILE", metavar="FILE")
    (options, args) = parser.parse_args()
    if options.filename != None:
        if not os.path.exists( options.filename): 
            print "The file does not exist or it is an incorrect filename: " + options.filename
            print ""
            usage(args) 
            sys.exit(-1)
        h4parser = H4MapParser(options.filename)
        h4parser.parse_content()

