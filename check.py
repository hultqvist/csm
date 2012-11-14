#!/usr/bin/python
# Copyright 2012 Peter Hultqvist, phq@silentorbit.com
# Distributed under the terms of the GNU Affero General Public License
#
# This file is called to make sure the rrd-files exists and create them if not
#
# Configuration:
# The variables in the begining can be modified to change interval for logging

import os, rrdtool, sys

# Minutes per month
month=44640
# minutes per year
year=35040*15

step = 60
heartbeat = 120

rra_month	= "RRA:AVERAGE:0.5:1:%i" % month
rra_month_min	= "RRA:MIN:0.5:1:%i" % month
rra_month_max	= "RRA:MAX:0.5:1:%i" % month
rra_year	= "RRA:AVERAGE:0.5:15:%i" % (year/15)
rra_year_min	= "RRA:MIN:0.5:15:%i" % (year/15)
rra_year_max	= "RRA:MAX:0.5:15:%i" % (year/15)

if __name__ == "__main__":
	print("\nThese checks are done automatically when update.py is run\n")
	sys.exit(-1)


def process_check(user):
	path = "rrd/user-"+user+".rrd"
	if os.path.exists(path):
		return

	print("Creating process rrd for user "+user)
	rrdtool.create(path, "--step", str(step),
		"DS:rss:GAUGE:%i:0:U" % heartbeat,
		"DS:vsz:GAUGE:%i:0:U" % heartbeat,
		"DS:pcpu:GAUGE:%i:0:U" % heartbeat,
		rra_month,
		rra_month_min,
		rra_month_max,
		rra_year,
		rra_year_min,
		rra_year_max
	)


def bean_check():
	path = "rrd/beancounters.rrd"
	if os.path.exists(path):
		return

	print("Creating process rrd for beancounters")
	rrdtool.create(path, "--step", str(step),
		"DS:kmemsize:GAUGE:%i:0:U" % heartbeat,
		"DS:kmemsize_fail:COUNTER:%i:0:U" % heartbeat,
		"DS:lockedpages:GAUGE:%i:0:U" % heartbeat,
		"DS:lockedpages_fail:COUNTER:%i:0:U" % heartbeat,
		"DS:privvmpages:GAUGE:%i:0:U" % heartbeat,
		"DS:privvmpages_fail:COUNTER:%i:0:U" % heartbeat,
		"DS:shmpages:GAUGE:%i:0:U" % heartbeat,
		"DS:shmpages_fail:COUNTER:%i:0:U" % heartbeat,
		"DS:numproc:GAUGE:%i:0:U" % heartbeat,
		"DS:numproc_fail:COUNTER:%i:0:U" % heartbeat,
		"DS:physpages:GAUGE:%i:0:U" % heartbeat,
		"DS:physpages_fail:COUNTER:%i:0:U" % heartbeat,
		"DS:vmguarpages:GAUGE:%i:0:U" % heartbeat,
		"DS:vmguarpages_fail:COUNTER:%i:0:U" % heartbeat,
		"DS:oomguarpages:GAUGE:%i:0:U" % heartbeat,
		"DS:oomguarpages_fail:COUNTER:%i:0:U" % heartbeat,
		"DS:numtcpsock:GAUGE:%i:0:U" % heartbeat,
		"DS:numtcpsock_fail:COUNTER:%i:0:U" % heartbeat,
		"DS:numflock:GAUGE:%i:0:U" % heartbeat,
		"DS:numflock_fail:COUNTER:%i:0:U" % heartbeat,
		"DS:numpty:GAUGE:%i:0:U" % heartbeat,
		"DS:numpty_fail:COUNTER:%i:0:U" % heartbeat,
		"DS:numsiginfo:GAUGE:%i:0:U" % heartbeat,
		"DS:numsiginfo_fail:COUNTER:%i:0:U" % heartbeat,
		"DS:tcpsndbuf:GAUGE:%i:0:U" % heartbeat,
		"DS:tcpsndbuf_fail:COUNTER:%i:0:U" % heartbeat,
		"DS:tcprcvbuf:GAUGE:%i:0:U" % heartbeat,
		"DS:tcprcvbuf_fail:COUNTER:%i:0:U" % heartbeat,
		"DS:othersockbuf:GAUGE:%i:0:U" % heartbeat,
		"DS:othersockbuf_fail:COUNTER:%i:0:U" % heartbeat,
		"DS:dgramrcvbuf:GAUGE:%i:0:U" % heartbeat,
		"DS:dgramrcvbuf_fail:COUNTER:%i:0:U" % heartbeat,
		"DS:numothersock:GAUGE:%i:0:U" % heartbeat,
		"DS:numothersock_fail:COUNTER:%i:0:U" % heartbeat,
		"DS:dcachesize:GAUGE:%i:0:U" % heartbeat,
		"DS:dcachesize_fail:COUNTER:%i:0:U" % heartbeat,
		"DS:numfile:GAUGE:%i:0:U" % heartbeat,
		"DS:numfile_fail:COUNTER:%i:0:U" % heartbeat,
		"DS:numiptent:GAUGE:%i:0:U" % heartbeat,
		"DS:numiptent_fail:COUNTER:%i:0:U" % heartbeat,
		rra_month,
		rra_month_min,
		rra_month_max,
		rra_year,
		rra_year_min,
		rra_year_max
		)

def cpu_check():
	path = "rrd/cpu.rrd"
	if os.path.exists(path):
		return

	print("Creating cpu rrd")
	rrdtool.create(path, "--step", str(step),
		"DS:user:COUNTER:%i:0:U" % heartbeat,
		"DS:nice:COUNTER:%i:0:U" % heartbeat,
		"DS:sys:COUNTER:%i:0:U" % heartbeat,
		"DS:idle:COUNTER:%i:0:U" % heartbeat,
		"DS:iowait:COUNTER:%i:0:U" % heartbeat,
		"DS:irq:COUNTER:%i:0:U" % heartbeat,
		"DS:softirq:COUNTER:%i:0:U" % heartbeat,
		rra_month,
		rra_month_min,
		rra_month_max,
		rra_year,
		rra_year_min,
		rra_year_max
	)

def net_check(interface):
	path = "rrd/net-%s.rrd" % interface
	if os.path.exists(path):
		return

	print("Creating net rrd")
	rrdtool.create(path, "--step", str(step),
		"DS:in:DERIVE:%i:0:U" % heartbeat,
		"DS:out:DERIVE:%i:0:U" % heartbeat,
		rra_month,
		rra_month_min,
		rra_month_max,
		rra_year,
		rra_year_min,
		rra_year_max
	)

def disk_check(device):
	path = "rrd/disk-"+device+".rrd"
	if os.path.exists(path):
		return

	print("Creating disk rrd")
	rrdtool.create(path, "--step", str(step),
		"DS:size:GAUGE:%i:0:U" % heartbeat,
		"DS:used:GAUGE:%i:0:U" % heartbeat,
		rra_month,
		rra_year
	)

def ping_check(host):
	path = "rrd/ping-"+host+".rrd"
	if os.path.exists(path):
		return

	rrdtool.create(path, "--step", str(step),
		"DS:rtt:GAUGE:%i:0:U" % heartbeat,
		rra_month,
		rra_month_min,
		rra_month_max,
		rra_year,
		rra_year_min,
		rra_year_max
		)

def mem_check():
	path = "rrd/mem.rrd"
	if os.path.exists(path):
		return

	rrdtool.create(path, "--step", str(step),
		"DS:used:GAUGE:%i:0:U" % heartbeat,
		"DS:buffers:GAUGE:%i:0:U" % heartbeat,
		"DS:cached:GAUGE:%i:0:U" % heartbeat,
		rra_month,
		rra_month_min,
		rra_month_max,
		rra_year,
		rra_year_min,
		rra_year_max
		)

