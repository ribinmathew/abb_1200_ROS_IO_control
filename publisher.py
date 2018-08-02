import rospy
from std_msgs.msg import Int32
import time
import requests
import re
import time
from bs4 import BeautifulSoup
session=requests.Session()
    
def talker():
        pub = rospy.Publisher('io_pins_status', Int32, queue_size=10)
        rospy.init_node('talker', anonymous=True)
        rate = rospy.Rate(10) # 10hz
        while not rospy.is_shutdown():
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
		

   
if __name__ == '__main__':
      try:
           talker()
      except rospy.ROSInterruptException:
          pass

