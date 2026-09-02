#!/usr/bin/env python3
# rs5_test.py
#
# use localnet  E459abb
#
# python -i ..\py3\startup.py

import requests
# import rwsuis
from rwsuis import RWS
# from clsRWS import RWS

norbert = 'http://152.94.160.198'
rudolf = 'http://152.94.160.197'

#  Hmmm
# c:>curl --digest -u "Default User":robotics "http://152.94.0.38/rw/panel/ctrlstate"
#                     ^
# SyntaxError: invalid syntax

auth=requests.auth.HTTPDigestAuth('Default User', 'robotics')
response = requests.get(norbert+"/rw/panel/ctrlstate", auth=auth)
print(response)
print(response.text)
response = requests.get(norbert+"/rw/panel/ctrlstate?json=1", auth=auth)

robot = RWS.RWS(norbert)
robot = RWS.RWS(rudolf)
# ?
(tr, rot) = robot.get_robtarget_variables( "p1" ) 
wrd = robot.get_rapid_variable( "WRD" ) 

new_rt = [0,0,314] 
robot.request_rmmp()
robot.set_robtarget_translation("target_K0", new_rt)   # a valid (VAR) robtarget in RAPID

wrd = 31
robot.set_rapid_variable( "WRD", wrd )

# exit()