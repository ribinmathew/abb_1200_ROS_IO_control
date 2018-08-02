
from __future__ import absolute_import

import socket
import select
from . import egm_pb2
import requests
from BeautifulSoup import BeautifulSoup
import traceback
from websocket import create_connection
from collections import namedtuple
import numpy as np
from datetime import datetime
import errno


class RAPID(object):

    def __init__(self, base_url='http://192.168.125.1:11000', username='Default User', password='robotics'):
        self.base_url=base_url
        self.auth=requests.auth.HTTPDigestAuth(username, password)

    def _do_get(self, relative_url):
        url="/".join([self.base_url, relative_url])
        res=requests.get(url, auth=self.auth)
        return self._process_response(res)

    def _do_post(self, relative_url, payload=None):
        url="/".join([self.base_url, relative_url])
        res=requests.post(url, data=payload, auth=self.auth)
        return self._process_response(res)

    def _process_response(self, response):        
        soup=BeautifulSoup(response.text)

        if (response.status_code == 500):
            raise Exception("Robot returning 500 Internal Server Error")
    

        if (response.status_code == 200 or response.status_code==204):
            return soup.body
        
        error_code=int(soup.find('span', attrs={'class':'code'}).text)
        error_message1=soup.find('span', attrs={'class': 'msg'})
        if (error_message1 is not None):
            error_message=error_message1.text
        else:
            error_message="Received error from ABB robot: " + str(error_code)

        raise ABBException(error_message, error_code)

    def start(self, cycle='asis'):
        payload={"regain": "continue", "execmode": "continue" , "cycle": cycle, "condition": "none", "stopatbp": "disabled", "alltaskbytsp": "false"}
        res=self._do_post("rw/rapid/execution?action=start", payload)

    def stop(self):
        payload={"stopmode": "stop"}
        res=self._do_post("rw/rapid/execution?action=stop", payload)

    def resetpp(self):
        res=self._do_post("rw/rapid/execution?action=resetpp")

    def get_execution_state(self):
        soup = self._do_get("rw/rapid/execution")
        ctrlexecstate=soup.find('span', attrs={'class': 'ctrlexecstate'}).text
        cycle=soup.find('span', attrs={'class': 'cycle'}).text
        return RAPIDExecutionState(ctrlexecstate, cycle)
    
    def get_controller_state(self):
        soup = self._do_get("rw/panel/ctrlstate")
        return soup.find('span', attrs={'class': 'ctrlstate'}).text
    
    def get_operation_mode(self):
        soup = self._do_get("rw/panel/opmode")        
        return soup.find('span', attrs={'class': 'opmode'}).text
    
    def get_digital_io(self, signal, network='Local', unit='DRV_1'):
        soup = self._do_get("rw/iosystem/signals/" + network + "/" + unit + "/" + signal)        
        state = soup.find('span', attrs={'class': 'lvalue'}).text
        return int(state)
    
    def set_digital_io(self, signal, value, network='Local', unit='DRV_1'):
        lvalue = '1' if bool(value) else '0'
        payload={'lvalue': lvalue}
        res=self._do_post("rw/iosystem/signals/" + network + "/" + unit + "/" + signal + "?action=set", payload)
    
    def get_rapid_variable(self, var):
        soup = self._do_get("rw/rapid/symbol/data/RAPID/T_ROB1/" + var)        
        state = soup.find('span', attrs={'class': 'value'}).text
        return state
    
    def set_rapid_variable(self, var, value):
        payload={'value': value}
        res=self._do_post("rw/rapid/symbol/data/RAPID/T_ROB1/" + var + "?action=set", payload)
        
    def read_event_log(self, elog=0):
        o=[]
        soup = self._do_get("rw/elog/" + str(elog) + "/?lang=en")
        state=soup.find('div', attrs={'class': 'state'})
        ul=state.find('ul')
        
        for li in ul.findAll('li'):
            def find_val(v):
                return li.find('span', attrs={'class': v}).text
            msg_type=int(find_val('msgtype'))
            code=int(find_val('code'))
            tstamp=datetime.strptime(find_val('tstamp'), '%Y-%m-%d T  %H:%M:%S')
            title=find_val('title')
            desc=find_val('desc')
            conseqs=find_val('conseqs')
            causes=find_val('causes')
            actions=find_val('actions')
            args=[]
            nargs=int(find_val('argc'))
            for i in xrange(nargs):
                arg=find_val('arg%d' % (i+1))
                args.append(arg)
            
            o.append(RAPIDEventLogEntry(msg_type,code,tstamp,args,title,desc,conseqs,causes,actions))
        return o

RAPIDExecutionState=namedtuple('RAPIDExecutionState', ['ctrlexecstate', 'cycle'], verbose=False)
RAPIDEventLogEntry=namedtuple('RAPIDEventLogEntry', ['msgtype', 'code', 'tstamp', 'args', 'title', 'desc', 'conseqs', 'causes', 'actions'])

class ABBException(Exception):
    def __init__(self, message, code):
        super(ABBException, self).__init__(message)
        self.code=code





