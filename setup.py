# mysetup.py
# -*- coding: utf-8 -*-
from distutils.core import setup
import py2exe



option={"py2exe" : 
            {"compressed": 3, 
             "optimize": 2, 
 #           "includes" : ["sip"],
             "bundle_files": 1  ,          
        #     "dll_excludes":["QtCore4.dll","QtGui4.dll"]
            }
       }

setup(
    version = "1.0",
    options=option,
    zipfile=None, 
#    data_files = data,
    console=[{"script": "weif.py"}])

