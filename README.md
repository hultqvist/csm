Complete System Monitoring

by Peter Hultqvist, phq@silentorbit.com

http://silentorbit.com/notes/

For the latest version, get it from the git repository

	git clone https://github.com/hultqvist/csm.git

This program uses rrdtool toghether with its own python code to collect and store running data about your system.
It is mostly aimed at OpenVZ VPS systems having a /proc/user_beancounters file but it will work fine on other systems as well.

# License

Copyright 2009 Peter Hultqvist
Distributed under the GNU Affero General Public License

# Requirements

 * python
 * rrdtool, both command line and python bindings
	
Ubuntu/Debian: apt-get install python rrdtool python-rrd

# Installation/Upgrade

Copy config-dist.py into config.py and change the contents within.

## For OpenVZ user_beancounters statistics:

/proc/user_beancounters is not readable by ordinary users, to read it:

1. move bean.sh to /root/bin/bean.sh

2. run visudo and add the following line:

	statuser            ALL=(ALL)       NOPASSWD: /root/bin/bean.sh

Where statuser is the username you will be running csm-update.py as.

# Collect data

Your system must be running update.py to collect data about you project.
The data is stored in rrd files in rrd/ which are created automatically.
	
csm-update is an init-script that can be used for this.

# Generate graphs

python graph.py [hours] [offset] [path-prefix]
Generates png images into the images folder for the last [hours], default 24.

A typical use case is found in graph-all.sh
