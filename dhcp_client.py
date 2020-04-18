from __future__ import print_function
import argparse 

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

	# for testing and diagnostic purposes 
	def show(self, packet):
		packet.show2() 
		return;

	#https://www.omnisecu.com/ccna-security/dhcp-starvation-attacks-and-dhcp-spoofing-attacks.php
	def detectDHCPStarvation(self):
		def callback(pkt):
			if DHCP in pkt and pkt[DHCP].options[0][1] == 1:
				print('DHCP DISCOVER \n %s MAC: %s' % (pkt[IP].src, pkt[Ether].src))

		pkt = sniff(prn=callback, store=0)

	#https://en.wikipedia.org/wiki/Rogue_DHCP
	#https://gist.github.com/joselitosn/a8a7b842037f9357fd56
	def serverCount(self): 
		def callback(pkt):
			if DHCP in pkt and pkt[DHCP].options[0][1] == 2:
				print('DHCP OFFER \nIP: %s MAC: %s' % (pkt[IP].src, pkt[Ether].src))

		self.dhcp_discover = Ether(dst=self.destMAC)/IP(src=self.srcIPAddr,dst=self.destIPAddr)/UDP(sport=self.srcPort,dport=self.destPort)/BOOTP(chaddr=self.srcMAC)/DHCP(options=[("message-type","discover"),"end"])
		sendp(self.dhcp_discover)
		pkt = sniff(prn=callback, store=0)

	def discover(self):
		#did not provide xid for this one
		self.dhcp_discover = Ether(dst=self.destMAC)/IP(src=self.srcIPAddr,dst=self.destIPAddr)/UDP(sport=self.srcPort,dport=self.destPort)/BOOTP(chaddr=self.srcMAC)/DHCP(options=[("message-type","discover"),"end"])

		#contains it's MAC address
		#destined for UDP port number 68
		#key values, message direction, sorce MAC address, destination MAC address, source IPv4 address; destination IPv4 address, source port number, destination port number
		
		print("SENT: Discover Packet")
		self.show(self.dhcp_discover)

		#srp1 only returns the first answer
		self.dhcp_offer = srp1(self.dhcp_discover, iface=self.iface, timeout=10)

		if self.dhcp_offer == None:
			self.dhcp_offer = -1
			print("timeout")
			return 
		else: 
			print("RECEIVED: Offer Packet")
			self.show(self.dhcp_offer)

		#this is the DHCP offer
		#the message contains offered TCP/IP configuration, like IPv4 address and subnet mask, accept the first one that arrives
		#key values; message direction, source MAC address, destination MAC address, source IPv4 address, destination IPv4 address, source port number, destination port number

	def request(self):

		my_ip = self.dhcp_offer[BOOTP].yiaddr
		server_ip = self.dhcp_offer[BOOTP].siaddr

		self.dhcp_request = Ether(src=self.srcMAC, dst=self.destMAC)/IP(src=self.srcIPAddr,dst=self.destIPAddr)/UDP(sport=self.srcPort,dport=self.destPort)/BOOTP(chaddr=self.srcMAC)/DHCP(options=[("message-type","request"),("server_id",server_ip),("requested_addr", my_ip),"end"])

		print("SENT: Request Packet")
		self.show(self.dhcp_request)

		#identify DHCPNak message to restart the process
		#constructs a DHCPACK datagram 
		#includes IP address and subnet mask for the DHCP client, may include other TCP/IP configuration, etc
		self.dhcp_ack = srp1(self.dhcp_request, iface=self.iface, timeout=10)

		if self.dhcp_ack == None:
			self.dhcp_ack = -1 
			print("timeout")
			return
		else: 
			print("RECEIVED: ACK Packet")
			self.show(self.dhcp_ack) 

		#accept first offer recieved by broadcasting a DHCP request message for the offered IPv4 address
		#contains the IP address of the server that issued the offer and the MAC address of the DHCP client
		#requests the selected DHCP server to assign the DHCP client an IP address and other TCP/IP configuration values 
		#also notifies that all other DHCP servers that there offers were not accepted by the DHCP client 
	
	def release(self):
		#at the end of the test, send a DHCPRelease packet to release the IP address and cancel the remaining lease
		my_ip = self.dhcp_offer[BOOTP].yiaddr
		server_ip = self.dhcp_offer[BOOTP].siaddr

		self.dhcp_release = Ether(dst=self.destMAC)/IP(src=self.srcIPAddr,dst=self.destIPAddr)/UDP(sport=self.srcPort,dport=self.destPort)/BOOTP(chaddr=self.srcMAC)/DHCP(options=[("message-type","release"),("server_id",server_ip),("requested_addr", my_ip),"end"])

		#self.show(self.dhcp_release)

		send(self.dhcp_release, iface=self.iface)

	def run(self): 
		self.discover()
		self.request()
		self.release() 


if __name__ == "__main__":
	parser = argparse.ArgumentParser(
	description="Show information relating to DHCP",
	formatter_class=argparse.RawDescriptionHelpFormatter)
	parser.add_argument("-d", "--detect", help="detect if a DHCP starvation attack is occuring", action="store_true", default=False) 
	parser.add_argument("-s", "--scan", help="identify all of the DNS servers contained within the network", action="store_true", default=False) 

	args = parser.parse_args()

	client = DHCPClient()

	if args.scan:
		client.serverCount()
	elif args.detect:
		client.detectDHCPStarvation()
	else: 
		client.run()