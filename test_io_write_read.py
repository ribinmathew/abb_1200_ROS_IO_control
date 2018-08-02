import requests
import re
import time
session=requests.Session()
import rospy
from std_msgs.msg import Int32
from bs4 import BeautifulSoup
#rospy.init_node('io_write')
io_value = None

def Callback(data):
    global io_value
    io_value = data.data





    
def talker():
        
        while not rospy.is_shutdown():
	   pub = rospy.Publisher('io_pins_status', Int32, queue_size=10)
           rospy.init_node('io_state', anonymous=True)
       	   rate = rospy.Rate(10) # 10hz
           try:
		a = session.get("http://192.168.125.1/rw/iosystem/signals/Input1",auth=requests.auth.HTTPDigestAuth('Default User','robotics'))
		
	   except:
		session=requests.Session()
		a = session.get("http://192.168.125.1/rw/iosystem/signals/Input1",auth=requests.auth.HTTPDigestAuth('Default User','robotics'))
	   ac = a.content
	

	   x = re.compile("<.+?>").findall(ac)
	
	   ac.replace(x[0],"")
	
	
	   dictval={}
	
	   soup  = BeautifulSoup(ac,'lxml')
	


	   for link in soup.find_all('li'):
		if not link:break
		title=link.get('title')
		dictval[title]={}
		soup2=BeautifulSoup(str(link))
		for llink in soup2.find_all('span'):
			dictval[title][llink.get('class')[0]]=llink.encode_contents()
		value1 = dictval['DeviceNet/d652/Input1']['lvalue']
		value = int(value1)
		

           	rospy.loginfo(value)
	   	pub.publish(value)
	   	rate.sleep()
			  
		rospy.Subscriber("io_pins_status", Int32, Callback)
		rate.sleep()
		

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
		     talker()
		     			   
		     
	    
		except rospy.ROSInterruptException:
       	      		pass
	
