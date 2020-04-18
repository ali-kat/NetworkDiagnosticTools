## README

### System Requirements 

This project was developed using Arch Linux 5.5.16 and Python 3.8.2. 

Please set up BCC on your system first by following these instructions:

https://github.com/iovisor/bcc/blob/master/INSTALL.md

After this, ensure that the following python modules are installed; 

bcc == 0.1.10 
Flask == 1.1.2 
flask-socketio == 4.2.1 
galileo-flask-socketio == 4.2.2.dev0 
scapy == git_archive.dev304758016

### File Structure

```bash
.
+-- static
|   +-- js
|   	+-- table.js
+-- templates
|   +-- index_dhcp.html
|   +-- index_dns.html
|   +-- index_solisten.html
|   +-- index_tcp.html
|   +-- index_tcpdrop.html
|   +-- index_tcpretrans.html
|   +-- index_tcptracer.html
+-- dhcp_app.py
+-- dhcp_client.py
+-- dns_app.py
+-- gethostlatency.py
+-- solisten.py
+-- solisten_app.py
+-- tcpdrop.py
+-- tcpdrop_app.py
+-- tcpretrans.py
+-- tcpretrans_app.py
+-- tcptracer.py
+-- tcptracer_app.py
+-- README.md
```

### How to Run

#### TCP Analysis Toolkit

"tcptracer.py"

```bash
sudo python tcptracer_app.py
```

"solisten.py"

```bash
sudo python solisten.py
```

"tcpretrans.py"

```bash
sudo python tcpretrans.py
```

"tcpdrop.py"

```bash
sudo python tcpdrop.py
```

To view the web content for all of these tools; follow the link displayed on the console; `http://127.0.0.1:5000/ `

#### DNS Analysis Toolkit

"gethostlatency.py"

```bash
sudo python dns_app.py
```

#### DHCP Analysis Toolkit 

"dhcp_app.py"

```bash
sudo python dhcp_app.py
```

"serverCount()"

```bash
sudo python dhcp_client.py -s
```

"detectDHCPStarvation()"

```bash
sudo python dhcp_client.py -d
```

