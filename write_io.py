import requests
import re
import time
session=requests.Session()
import rospy
from std_msgs.msg import Int32
from bs4 import BeautifulSoup

io_value = None

def Callback(data):
    global io_value
    io_value = data.data








def io_write():
	
	while not rospy.is_shutdown():
		rospy.init_node('io_write')
   		rospy.Subscriber("io_pins_status", Int32, Callback)
   		rospy.sleep(1)
		

		value = io_value
		print(value)

		try:
			r = session.post("http://192.168.125.1/rw/iosystem/signals/DeviceNet/d652/Output3?action=set", data={'lvalue': value},auth=requests.auth.HTTPDigestAuth('Default User','robotics'))
			replay = r.status_code
			if str(replay) == "204":
				print("OK")
			
		except:
			session=requests.Session()
			r = session.post("http://192.168.125.1/rw/iosystem/signals/DeviceNet/d652/Output3?action=set", data={'lvalue': value},auth=requests.auth.HTTPDigestAuth('Default User','robotics'))
			print(r.status_code, r.reason)
		

		

	
if __name__ == '__main__':

		try:	
		    
		   
		     io_write()
	    
		except rospy.ROSInterruptException:
       	      		pass
	
