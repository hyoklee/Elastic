# Return fill value that has uint32 type.
curl -XGET 'http://localhost:9200/myang64/_search?q=(VarAttrName:_FillValue)AND(AttrDtype:uint32)'


