#!/usr/bin/env python
# -*- coding: utf-8 -*-
###########################################################################
# Copyright (C) 2017 The HDF Group
#
# Author: Hyo-Kyung Lee (hyoklee@hdfgroup.org)
#
# Last Update: 2017/01/24
###########################################################################
"""
   This module parses an OPeNDAP DMR++ file and generates binary streams
   from HDF5 file.

   The binary streams are saved with MD5 file name.
"""

import lxml.etree as etree
import unittest
import hashlib
import os
import numpy as np
import ast
import string
import glob

class OPeNDAPParser(object):

    """OPeNDAP parser class"""

    def __init__(self, ddx_file, remote=True):
        """ Constructor

        @param ddx_file: OPeNDAP DDX output file
        """

        self.xml_file = ddx_file
        self.remote = remote
        self.binary_file_path = 'bytestream'
        self.depth = 0
        self.tree = None
        self.last = "group"
        # Type map is based on the following document:
        # 
        # http://docs.opendap.org/index.php/DAP4:_Specification_Volume_1#Appendix_1._DAP4_DMR_Syntax_as_a_RELAX_NG_Schema
        #
        # UByte is from legacy dap4 schema and example.
        self.type_hash_map = {"Byte": "uint8",
                              "UByte": "uint8",
                              "Int8": "int8",
                              "UInt8": "uint8",
                              "Int16": "int16",
                              "UInt16": "uint16",
                              "Int32": "int32",
                              "UInt32": "uint32",
                              "Int64": "int64",                              
                              "UInt64": "uint64",
                              "Url": "string",
                              "Float32": "float32",
                              "Float64": "float64",
                              "String": "string",
                              "Structure": "compound"}

        try:
            if self.remote:
                self.tree = etree.fromstring(self.xml_file)
                self.fname = self.tree.attrib['name']+'.ddx'
            else:
                self.tree = etree.parse(self.xml_file).getroot()
                
                
        except etree.XMLSyntaxError as err:
            print "The OPeNDAP DDX file is not valid:"
            print self.xml_file
            print err
            return None
        except IOError as err:
            print 'ERROR:Can\'t read the OPeNDAP file :' + self.xml_file
            print err
            return None

        self.schema = "{http://xml.opendap.org/ns/DAP/3.2#}"
        self.h4schema = "{http://www.hdfgroup.org/HDF4/XML/schema/HDF4map/1.0.1}"
        self.group_stack = []
        self.dims = {}

    def parse_content(self, conv=[], test=False):
        """Parses the OPeNDAP DDX."""

        # OPeNDAP's schema can vary from 3.2, 3.3 to 4.0.
        # Determine it from XML file.
        self.schema = self.tree.tag.split('}')[0]+'}'
        self.file_path = self.tree.attrib['name']
        self.recursive_walk(self.tree, self.depth)

            
    def create_dataset_dap4_array(self, node, key):
        """Create bytestreams in HDF5 dataset for DAP 4.0 array."""
        dname = node.attrib['name']
        # print dname
        namespaces = {'h4': 'http://www.hdfgroup.org/HDF4/XML/schema/HDF4map/1.0.1'}
        chunks_node = node.find("h4:chunks", namespaces)

        if chunks_node is not None:
            for c_node in chunks_node.getchildren():
                if (c_node.tag == (self.h4schema + "byteStream")):
                    self.parse_byteStream(c_node, c_node.attrib['chunkPositionInArray'])        
        dset = None
        return dset

    def parse_byteStream(self, bnode, chunk_p=None):
        """Parse byteStream tag.
        """
        if (bnode.tag == (self.h4schema + "byteStream")):
            self.offset = int(bnode.attrib['offset'])
            self.nBytes = int(bnode.attrib['nBytes'])
            self.file_handler=file(self.file_path,"rb")            
            self.file_handler.seek(self.offset)
            buf = self.file_handler.read(self.nBytes)
            hash = hashlib.md5()
            hash.update(buf)
            self.md5 =  hash.hexdigest()

            if (self.md5 != bnode.attrib['md5']):
                print 'Checksum does not match.'
            else:
                with open(self.binary_file_path+'/'+self.md5, 'wb') as bfile:
                    bfile.write(buf)

    
    def recursive_walk(self, root_node, depth):
        """This recursive function traverse the XML document using the
        ElementTree API; all the nodess are stored in a tree-like structure.

        @param root_node: lxml root node of the map file
        @param depth: used to keep track of the recursion level, 0 on the root.
        """
        self.depth = depth
        
        for node in root_node.getchildren():
            for key in self.type_hash_map:
                if node.tag == self.schema + key:
                    dset = self.create_dataset_dap4_array(node, key)
                    if dset:
                        self.last = "variable"
  
            if len(node) > 0:
                self.recursive_walk(node, self.depth + 1)
                self.depth = self.depth - 1


class TestOPeNDAPParser(unittest.TestCase):
    """Unit test"""

    def setUp(self):
        """set file name."""
        self.parser = OPeNDAPParser('test.dmrpp', False)

    def test_parser(self):
        """test parser.

        To run test, remove lines that refer to self.hpd first.
        """
        self.parser.parse_content()


if __name__ == '__main__':
    # unittest.main()
    for filename in glob.glob('*.dmrpp'):
        print filename
        parser = OPeNDAPParser(filename, False)        
        parser.parse_content()
        
