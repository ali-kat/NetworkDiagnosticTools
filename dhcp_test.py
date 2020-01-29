#todo: timeout when listening for a response 
#todo: listen for nak packets, restart process if one is recieved
#todo: validate TCP/IP parameters and send DECLINE packet if invalid, restart process
#todo: provide support for both versions; IPv4 and IPv6
#todo: improve SHOW method so it better show relevant information 
#todo: serverCount, display information of all DNS servers 
#todo: is the INFORM packet even relevant to this program? 
#todo: provide support for CLI arguments, specifying verbosity, versions, specify that you may only want to see information from the recieved packets, etc.

from __future__ import print_function
from scapy.all import * 

class DHCPClient: 
	def __init__(self):
		conf.checkIPaddr = False
		# normally Scapy makes sure that replies come from the same IP address the stimulus was sent to, however our DHCP packet was set to the IP broadcast address and any answer packet will have the IP address of the replying DHCP server as its source IP address
		# tl;dr the IP addresses wont match

		self.dhcp_discover = None
		self.dhcp_offer = None
		self.dhcp_request = None
		self.dhcp_ack = None
		# other DHCP packets here; decline, and inform
		self.dhcp_release = None

		self.iface = conf.iface
		self.srcMAC = get_if_raw_hwaddr(conf.iface)[1]
		self.destMAC = 'ff:ff:ff:ff:ff:ff' #broadcast MAC
		self.srcIPAddr = '0.0.0.0'
		self.destIPAddr = '255.255.255.255' #limited broadcast
		self.srcPort = 68
		self.destPort = 67

	def show(self, packet):
		#print(packet[BOOTP].xid)
		#print(packet[BOOTP].secs)
		#print(packet[BOOTP].flags)
		#print(packet[BOOTP].ciaddr)
		#print(packet[BOOTP].yiaddr)
		#print(packet[BOOTP].siaddr)
		#print(packet[BOOTP].giaddr)
		#print(packet[BOOTP].chaddr)
		#print(packet[BOOTP].sname)
		#print(packet[BOOTP].file)
		#print(packet[BOOTP].options)
		print(packet.display()) 

	#https://en.wikipedia.org/wiki/Rogue_DHCP
	def serverCount(self): 
		print()
		#there should be a method to check for multiple servers and report if that is the case
		#check for multiple DHCP servers 
		#ans, unans = srp(dhcp_discover, multi=True)
		#ans.summary();

	def discover(self):
		#did not provide xid for this one
		self.dhcp_discover = Ether(dst=self.destMAC)/IP(src=self.srcIPAddr,dst=self.destIPAddr)/UDP(sport=self.srcPort,dport=self.destPort)/BOOTP(chaddr=self.srcMAC)/DHCP(options=[("message-type","discover"),"end"])

		#contains it's MAC address
		#destined for UDP port number 68
		#key values, message direction, sorce MAC address, destination MAC address, source IPv4 address; destination IPv4 address, source port number, destination port number
		self.show(self.dhcp_discover)

		#srp1 only returns the first answer
		self.dhcp_offer = srp1(self.dhcp_discover, iface=self.iface)

		self.show(self.dhcp_offer)

		#this is the DHCP offer
		#the message contains offered TCP/IP configuration, like IPv4 address and subnet mask, accept the first one that arrives
		#key values; message direction, source MAC address, destination MAC address, source IPv4 address, destination IPv4 address, source port number, destination port number

	def request(self):

		my_ip = self.dhcp_offer[BOOTP].yiaddr
		server_ip = self.dhcp_offer[BOOTP].siaddr

		self.dhcp_request = Ether(src=self.srcMAC, dst=self.destMAC)/IP(src=self.srcIPAddr,dst=self.destIPAddr)/UDP(sport=self.srcPort,dport=self.destPort)/BOOTP(chaddr=self.srcMAC)/DHCP(options=[("message-type","request"),("server_id",server_ip),("requested_addr", my_ip),"end"])

		self.show(self.dhcp_request)

		#identify DHCPNak message to restart the process
		#constructs a DHCPACK datagram 
		#includes IP address and subnet mask for the DHCP client, may include other TCP/IP configuration, etc
		self.dhcp_ack = srp1(self.dhcp_request, iface=self.iface)

		self.show(self.dhcp_ack) 

		#accept first offer recieved by broadcasting a DHCP request message for the offered IPv4 address
		#contains the IP address of the server that issued the offer and the MAC address of the DHCP client
		#requests the selected DHCP server to assign the DHCP client an IP address and other TCP/IP configuration values 
		#also notifies that all other DHCP servers that there offers were not accepted by the DHCP client 
	
	def decline(self):
		print() 
		#if the offered TCP/IP configuration parameters are invalid, send DHCPDecline packet, and restart process

	def release(self):
		#at the end of the test, send a DHCPRelease packet to release the IP address and cancel the remaining lease
		my_ip = self.dhcp_offer[BOOTP].yiaddr
		server_ip = self.dhcp_offer[BOOTP].siaddr

		self.dhcp_release = Ether(dst=self.destMAC)/IP(src=self.srcIPAddr,dst=self.destIPAddr)/UDP(sport=self.srcPort,dport=self.destPort)/BOOTP(chaddr=self.srcMAC)/DHCP(options=[("message-type","release"),("server_id",server_ip),("requested_addr", my_ip),"end"])

		self.show(self.dhcp_release)

		send(self.dhcp_release, iface=self.iface)

	def run(self): 
		self.discover()
		self.request()
		self.release() 

def main():
	client = DHCPClient()
	client.run()


main()