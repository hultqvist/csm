#!/usr/bin/python
# Copyright 2009 Peter Hultqvist, phq@endnode.se
# Distributed under the terms of the GNU Affero General Public License
#
# Complete System Monitoring
# Data collection program
# This program collects the data and store it in the database

import os

# Default settings
pinghosts = []
if(os.path.exists("config.py")):
	from config import *

import rrdtool, sys, re, time, subprocess
from check import *

reline = re.compile('[^a-z]*([a-z]+) *([0-9]+) *[0-9]+ *[0-9]+ *[0-9]+ *([0-9]+) *')

#OpenVZ
parameters = [
	"kmemsize",
	"lockedpages",
	"privvmpages",
	"shmpages",
	"numproc",
	"physpages",
	"vmguarpages",
	"oomguarpages",
	"numtcpsock",
	"numflock",
	"numpty",
	"numsiginfo",
	"tcpsndbuf",
	"tcprcvbuf",
	"othersockbuf",
	"dgramrcvbuf",
	"numothersock",
	"dcachesize",
	"numfile",
	"numiptent",
	]

def beanlog():
	if os.path.exists("/proc/user_beancounters") == False:
		return;	# We are not on an openvz system

	bean_check()
	# Read user_beancounters data
	file = os.popen("sudo /root/bin/bean.sh")
	#file = open('user_beancounters', 'r')
	line = file.readline()
	print line,

	held = {}
	fail = {}
	while line:
		line = file.readline()
		m = reline.match(line)
		if m:
			held[m.group(1)] = m.group(2)
			fail[m.group(1)] = m.group(3)
#		else:
#			print "None: " + line,
	file.close()

	# Write the data
	data = "N"

	for param in parameters:
		data = data + ":"+held[param]
		data = data + ":"+fail[param]

	rrdtool.update('rrd/beancounters.rrd', data)


recpuload = re.compile('^cpu +([0-9]*) ([0-9]*) ([0-9]*) ([0-9]*) ([0-9]*) ([0-9]*) ([0-9]*)')
def cpulog():
	cpu_check()

	file = open('/proc/stat', 'r')
	line = file.readline()
	load = recpuload.match(line)

	data = 'N'
	for n in range(0, 7):
		data += ':'+load.group(n+1)
	print "CPU: " + data
	rrdtool.update('rrd/cpu.rrd', data)

renet = re.compile('^ *([^ ]+): *([0-9]+) +[0-9]+ +[0-9]+ +[0-9]+ +[0-9]+ +[0-9]+ +[0-9]+ +[0-9]+ +([0-9]+) .*')
def netlog():
	# Read network traffic
	file = open('/proc/net/dev', 'r')
	while 1:
		line = file.readline()
		if not line:
			break

		net = renet.match(line)
		if net:
			net_check(net.group(1))
			print("Network: " + net.group(1))
			print("	 in: "+str(int(net.group(2))/1024))
			print("	out: "+str(int(net.group(3))/1024))
			data = 'N:'+net.group(2)+':'+net.group(3)
			rrdtool.update('rrd/net-'+net.group(1)+'.rrd', data)

def processlog():
	# Read process memory usage
	pcpu = {}
	rss = {}
	vsz = {}
	file = os.popen("ps -e -o user,rss,vsz,pcpu")
	#read header
	line = file.readline()

	# reading all lines
	line = file.readline()
	while line:
		cols = line.split()
		if cols[0] == "121" :
			cols[0] = "tor"
		try:
			rss[cols[0]] += int(cols[1])
			vsz[cols[0]] += int(cols[2])
			pcpu[cols[0]] += float(cols[3])
		except:
			rss[cols[0]] = int(cols[1])
			vsz[cols[0]] = int(cols[2])
			pcpu[cols[0]] = float(cols[3])
			print "User: " + cols[0], cols[1]
		line = file.readline()
	file.close()

	for user in pcpu:
		process_check(user)
		data = "N:" + str(rss[user]*1024) + ":" + str(vsz[user]*1024) + ":" + str(pcpu[user])
		print user,data
		rrdtool.update('rrd/user-'+user+'.rrd', data)

def pinglog():

	# Measure remote ping rtt
	reping = re.compile('^rtt .* = ([0-9\.]+)/([0-9\.]+)/([0-9\.]+)/([0-9\.]+) ms$')

	rtt_res = {}
	for host in pinghosts:
		rtt_res[host] = subprocess.Popen(['ping', '-c', '3', '-W', '3', '-q', host], stdout=subprocess.PIPE)

	for host in pinghosts:
		rtt = "INF"
		if (rtt_res[host].wait() == 0):
			#get rtt from output
			out = rtt_res[host].communicate()[0].splitlines()[-1]
			match = reping.match(out)
			if (match):
				rtt = str(float(match.group(2))/1000)

		data = "N:" + rtt
		print("ping: "+host+" "+data)
		ping_check(host)
		rrdtool.update('rrd/ping-'+host+'.rrd', data)

def memlog():
	# Measure remote ping rtt
	remem = re.compile('^Mem: +([0-9]+) +([0-9]+) +([0-9]+) +([0-9]+) +([0-9]+) +([0-9]+)')

	mem_check()
	res = subprocess.Popen(['free', '-b'], stdout=subprocess.PIPE)
	if (res.wait() == 0):
		out = res.communicate()[0].splitlines()[1]
		match = remem.match(out)
		used = int(match.group(2))
		buffers = int(match.group(5))
		cached = int(match.group(6))
		used = used - buffers - cached
		data = "N:" + str(used) + ":" + str(buffers) + ":"+str(cached)
		print("mem: "+data)
		os.system('rrdtool update rrd/mem.rrd '+data)
		print('rrdtool update rrd/mem.rrd '+data)

def disklog():
	# Measure disk usage
	redisk = re.compile('^/dev/([a-z0-9]+) +([0-9]+) +([0-9]+) +([0-9]+)')

	res = subprocess.Popen(['df', '-B', '1'], stdout=subprocess.PIPE)
	if (res.wait() != 0):
		return

	out = res.communicate()[0].splitlines()
	for l in out:
		match = redisk.match(l)
		if (match == None):
			continue

		dev = match.group(1)
		size = int(match.group(2))
		used = int(match.group(3))
		data = "N:" + str(size) + ":" + str(used)

		disk_check(dev)

		print("disk: "+dev+", "+data)
		os.system('rrdtool update rrd/disk-'+dev+'.rrd '+data)
		print('rrdtool update rrd/disk-'+dev+'.rrd '+data)

while 1:
	disklog()
	memlog()
	pinglog()
	beanlog()
	cpulog()
	processlog()
	netlog()

	print("...")
	# Wait remainder of every 10 seconds
	time.sleep(time.time() % 10)
