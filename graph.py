#!/usr/bin/python
# Copyright 2012 Peter Hultqvist, phq@silentorbit.com
# Distributed under the terms of the GNU Affero General Public License
#
# Complete System Monitoring
# Graph creation script
# Run this to greate images from the data
# adjust which parameters to generate graphs from by adding or removing comment #
import rrdtool, time, os, re, sys, glob

# Default settings
pinghosts = []
if(os.path.exists("config.py")):
	from config import *

shift = 0
interval = 24
prefix = "images"
if len(sys.argv) > 1:
	interval = int(sys.argv[1])
if len(sys.argv) > 2:
	shift = int(sys.argv[2])
if len(sys.argv) > 3:
	prefix = sys.argv[3]

print str(interval/3600) + "timmar"

interval *= 3600
shift *= 3600

start = str(int(time.time())-interval-shift)
end   = str(int(time.time())-shift)
cmd_common = ' -E --start='+start+' --end='+end+' '


#System memory
print ("Sysmem")
cmd = 'rrdtool graph '+prefix+'/mem.png '+cmd_common
cmd += '--title "System memory usage" -l0 -M -b 1024 '
cmd += ' DEF:used=rrd/mem.rrd:used:AVERAGE'
cmd += ' DEF:buffers=rrd/mem.rrd:buffers:AVERAGE'
cmd += ' DEF:cached=rrd/mem.rrd:cached:AVERAGE'
cmd += ' DEF:used_min=rrd/mem.rrd:used:MIN'
cmd += ' DEF:buffers_min=rrd/mem.rrd:buffers:MIN'
cmd += ' DEF:cached_min=rrd/mem.rrd:cached:MIN'
cmd += ' DEF:used_max=rrd/mem.rrd:used:MAX'
cmd += ' DEF:buffers_max=rrd/mem.rrd:buffers:MAX'
cmd += ' DEF:cached_max=rrd/mem.rrd:cached:MAX'

cmd += ' CDEF:bo=used,UN,INF,0,IF'
cmd += ' AREA:bo#DDDDDD:'

cmd += ' CDEF:bmin=used,buffers_min,+'
cmd += ' CDEF:bmax=used,buffers_max,+'
cmd += ' CDEF:bsum=used,buffers,+'
cmd += ' CDEF:cmin=bsum,cached_min,+'
cmd += ' CDEF:cmax=bsum,cached_max,+'
cmd += ' CDEF:csum=bsum,cached,+'

cmd += ' AREA:csum#ffff00:"Cached " '
cmd += ' AREA:cmin#cccc00 '
cmd += ' VDEF:maxC=cached_max,MAXIMUM'
cmd += ' VDEF:minC=cached_min,MINIMUM'
cmd += ' VDEF:avgC=cached,AVERAGE'
cmd += ' GPRINT:minC:"Min %6.2lf %sB"'
cmd += ' GPRINT:avgC:"Avg %6.2lf %sB"'
cmd += ' GPRINT:maxC:"Max %6.2lf %sB\\n"'

cmd += ' AREA:bsum#0000ff:"Buffers" '
cmd += ' AREA:bmin#0000cc '
cmd += ' VDEF:maxB=buffers_max,MAXIMUM'
cmd += ' VDEF:minB=buffers_min,MINIMUM'
cmd += ' VDEF:avgB=buffers,AVERAGE'
cmd += ' GPRINT:minB:"Min %6.2lf %sB"'
cmd += ' GPRINT:avgB:"Avg %6.2lf %sB"'
cmd += ' GPRINT:maxB:"Max %6.2lf %sB\\n"'

cmd += ' AREA:used#00ff00:"Used   " '
cmd += ' AREA:used_min#00cc00 '
cmd += ' VDEF:maxU=used_max,MAXIMUM'
cmd += ' VDEF:minU=used_min,MINIMUM'
cmd += ' VDEF:avgU=used,AVERAGE'
cmd += ' GPRINT:minU:"Min %6.2lf %sB"'
cmd += ' GPRINT:avgU:"Avg %6.2lf %sB"'
cmd += ' GPRINT:maxU:"Max %6.2lf %sB\\n"'

cmd += ' LINE1:cmax#888800 '
cmd += ' LINE1:bmax#000088 '
cmd += ' LINE1:used_max#008800 '

os.system(cmd)


#Ping rtt
for host in pinghosts:
	print("ping: " + host)
	cmd = 'rrdtool graph '+prefix+'/ping-'+host+'.png '+cmd_common
	cmd += '--title "Ping: '+host+'" -l0 -M -b 1024 '
	cmd += ' DEF:rtt=rrd/ping-'+host+'.rrd:rtt:AVERAGE'
	cmd += ' DEF:rtt_min=rrd/ping-'+host+'.rrd:rtt:MIN'
	cmd += ' DEF:rtt_max=rrd/ping-'+host+'.rrd:rtt:MAX'

	cmd += ' AREA:rtt_max#ff00ff:"RTT" '
	cmd += ' AREA:rtt_min#cc00cc '
	cmd += ' LINE1:rtt#000000 '
	cmd += ' VDEF:max=rtt_max,MAXIMUM'
	cmd += ' VDEF:min=rtt_min,MINIMUM'
	cmd += ' VDEF:avg=rtt,AVERAGE'
	cmd += ' GPRINT:min:"Min %6.2lf %ss"'
	cmd += ' GPRINT:avg:"Avg %6.2lf %ss"'
	cmd += ' GPRINT:max:"Max %6.2lf %ss\\n"'

	cmd += ' CDEF:bi=rtt,INF,EQ,INF,0,IF'
	cmd += ' AREA:bi#ff0000:'

	cmd += ' CDEF:bo=rtt,UN,INF,0,IF'
	cmd += ' AREA:bo#DDDDDD:'

	os.system(cmd)


#Beancounters

parameters = [ # remove "#" sig to enable parameters, add to disable
#	"kmemsize",
#	"lockedpages",
#	"privvmpages",
#	"shmpages",
#	"numproc",
#	"physpages",
#	"vmguarpages",
#	"oomguarpages",
#	"numtcpsock",
#	"numflock",
#	"numpty",
#	"numsiginfo",
#	"tcpsndbuf",
#	"tcprcvbuf",
#	"othersockbuf",
#	"dgramrcvbuf",
#	"numothersock",
#	"dcachesize",
#	"numfile",
#	"numiptent",
	]
if len(parameters) > 0:
	#Get maximum values for all parameters
	#Barrier
	reline = re.compile('.* ([a-z]+) *[0-9]+ *[0-9]+ *([0-9]+) *[0-9]+ *[0-9]+ *')

	file = os.popen("sudo /root/bin/bean.sh")
	line = file.readline()
	barrier = {}
	while line:
		line = file.readline()
		m = reline.match(line)
		if m:
			barrier[m.group(1)] = m.group(2)
	file.close()

#Generate beancounter graphs
for param in parameters:
	upper = barrier[param]

	cmd = 'rrdtool graph '+prefix+'/'+param+'.png '+cmd_common
	cmd += '--title '+param+' -u'+upper+' -l0 -b 1024 '
	cmd += 'DEF:val=rrd/beancounters.rrd:'+param+':AVERAGE '
	cmd += 'DEF:val=_min=rrd/beancounters.rrd:'+param+':MIN '
	cmd += 'DEF:val=_max=rrd/beancounters.rrd:'+param+':MAX '
	cmd += 'DEF:val=_fail=rrd/beancounters.rrd:'+param+'_fail:AVERAGE '
	cmd += 'CDEF:bo=val,UN,INF,0,IF '
	cmd += 'AREA:bo#DDDDDD: '
	cmd += 'HRULE:'+barrier[param]+'#FF0000 '
	cmd += 'AREA:val_max#00FF00:"max" '
	cmd += 'AREA:val_min#00bb00:"min" '
	cmd += 'LINE1:val#000000 '
	cmd += 'CDEF:sc_fail=val_fail,100,* '
	cmd += 'LINE2:sc_fail#FF00FF:"failcount" '
	os.system(cmd)


# CPU
cmd = 'rrdtool graph '+prefix+'/cpu.png '+cmd_common
cmd += '--title "CPU usage" -u100 -l0 -M '
cpugr = [
	'DEF:uj=rrd/cpu.rrd:user:AVERAGE',
	'DEF:nj=rrd/cpu.rrd:nice:AVERAGE',
	'DEF:sj=rrd/cpu.rrd:sys:AVERAGE',
	'DEF:ij=rrd/cpu.rrd:idle:AVERAGE',
	'DEF:wj=rrd/cpu.rrd:iowait:AVERAGE',
	'DEF:qj=rrd/cpu.rrd:irq:AVERAGE',
	'DEF:oj=rrd/cpu.rrd:softirq:AVERAGE',
	'CDEF:l=uj,0.1,0.1,IF',
	'CDEF:bo=uj,UN,INF,0,IF',
	'AREA:bo#DDDDDD:',
	'CDEF:tj=uj,nj,+,sj,+,ij,+,wj,+,qj,+,oj,+',
	'CDEF:usr=100,uj,*,tj,/',
	'CDEF:nic=100,nj,*,tj,/',
	'CDEF:sys=100,sj,*,tj,/',
	'CDEF:idl=100,ij,*,tj,/',
	'CDEF:iow=100,wj,*,tj,/',
	'CDEF:irq=100,qj,*,tj,/',
	'CDEF:sir=100,oj,*,tj,/',

	'AREA:sys#90C5CC:"System "',
#	'LINE2:l#70A5AC::STACK',
	'VDEF:maxS=sys,MAXIMUM',
	'VDEF:minS=sys,MINIMUM',
	'VDEF:avgS=sys,AVERAGE',
	'GPRINT:maxS:"Max %6.2lf%%"',
	'GPRINT:minS:"Min %6.2lf%%"',
	'GPRINT:avgS:"Avg %6.2lf%%\\n"',

	'AREA:usr#B0E5EC:"User   ":STACK',
#	'LINE2:l#90C5CC::STACK',
	'VDEF:maxU=usr,MAXIMUM',
	'VDEF:minU=usr,MINIMUM',
	'VDEF:avgU=usr,AVERAGE',
	'GPRINT:maxU:"Max %6.2lf%%"',
	'GPRINT:minU:"Min %6.2lf%%"',
	'GPRINT:avgU:"Avg %6.2lf%%\\n"',

	'AREA:nic#0040A2:"Nice   ":STACK',
	'VDEF:maxN=nic,MAXIMUM',
	'VDEF:minN=nic,MINIMUM',
	'VDEF:avgN=nic,AVERAGE',
	'GPRINT:maxN:"Max %6.2lf%%"',
	'GPRINT:minN:"Min %6.2lf%%"',
	'GPRINT:avgN:"Avg %6.2lf%%\\n"',

	'AREA:iow#BBBBBB:"IOWait ":STACK',
	'VDEF:maxW=iow,MAXIMUM',
	'VDEF:minW=iow,MINIMUM',
	'VDEF:avgW=iow,AVERAGE',
	'GPRINT:maxW:"Max %6.2lf%%"',
	'GPRINT:minW:"Min %6.2lf%%"',
	'GPRINT:avgW:"Avg %6.2lf%%\\n"',

	'AREA:irq#EEFF00:"IRQ    ":STACK',
	'VDEF:maxQ=irq,MAXIMUM',
	'VDEF:minQ=irq,MINIMUM',
	'VDEF:avgQ=irq,AVERAGE',
	'GPRINT:maxQ:"Max %6.2lf%%"',
	'GPRINT:minQ:"Min %6.2lf%%"',
	'GPRINT:avgQ:"Avg %6.2lf%%\\n"',

	'AREA:sir#EE00FF:"SoftIRQ":STACK',
	'VDEF:maxO=sir,MAXIMUM',
	'VDEF:minO=sir,MINIMUM',
	'VDEF:avgO=sir,AVERAGE',
	'GPRINT:maxO:"Max %6.2lf%%"',
	'GPRINT:minO:"Min %6.2lf%%"',
	'GPRINT:avgO:"Avg %6.2lf%%\\n"',

	'AREA:idl#EEFFFF:"Idle   ":STACK',
	'VDEF:maxI=idl,MAXIMUM',
	'VDEF:minI=idl,MINIMUM',
	'VDEF:avgI=idl,AVERAGE',
	'GPRINT:maxI:"Max %6.2lf%%"',
	'GPRINT:minI:"Min %6.2lf%%"',
	'GPRINT:avgI:"Avg %6.2lf%%\\n"',

]
for cpuln in  cpugr:
	cmd += cpuln + ' '
os.system(cmd)


# Network
for interface in os.listdir('rrd/'):
	if interface.startswith('net') == False:
		continue
	if interface.endswith('.rrd') == False:
		continue

	interface = interface[4:-4]

	print('Network: ' + interface)

	cmd = 'rrdtool graph '+prefix+'/net-'+interface+'.png '+cmd_common
	cmd += '--title "Network traffic: '+interface+'" '
	cmd += 'DEF:in=rrd/net-'+interface+'.rrd:in:AVERAGE '
	cmd += 'DEF:out=rrd/net-'+interface+'.rrd:out:AVERAGE '
	cmd += 'DEF:min_in=rrd/net-'+interface+'.rrd:in:MIN '
	cmd += 'DEF:min_out=rrd/net-'+interface+'.rrd:out:MIN '
	cmd += 'DEF:max_in=rrd/net-'+interface+'.rrd:in:MAX '
	cmd += 'DEF:max_out=rrd/net-'+interface+'.rrd:out:MAX '
	cmd += 'CDEF:bi=in,UN,INF,0,IF '
	cmd += 'AREA:bi#DDDDDD: '
	cmd += 'CDEF:bo=out,UN,-INF,0,IF '
	cmd += 'AREA:bo#DDDDDD: '

	cmd += 'CDEF:diff=out,in,- '
	cmd += 'VDEF:intot=in,TOTAL '
	cmd += 'VDEF:outtot=out,TOTAL '
	cmd += 'VDEF:inavg=in,AVERAGE '
	cmd += 'VDEF:outavg=out,AVERAGE '

	cmd += 'COMMENT:"      Average       Total     Diff Avg   Diff Tot\\n" '

	# In
	cmd += 'CDEF:sc_in=in,-1,* '
	cmd += 'CDEF:sc_min_in=min_in,-1,* '
	cmd += 'CDEF:sc_max_in=max_in,-1,* '
	cmd += 'AREA:sc_max_in#00ffff '
	cmd += 'AREA:sc_min_in#00cccc:"In " '
	cmd += 'LINE1:sc_in#000000 '
	cmd += 'GPRINT:inavg:"%6.2lf %sB" '
	cmd += 'GPRINT:intot:"%6.2lf %sB" '

	# Diff in
	cmd += 'CDEF:diffin=diff,0,GT,0,diff,-1,*,IF '
	cmd += 'VDEF:diffintot=diffin,TOTAL '
	cmd += 'VDEF:diffinavg=diffin,AVERAGE '
	cmd += 'GPRINT:diffinavg:"%6.2lf %sB" '
	cmd += 'GPRINT:diffintot:"%6.2lf %sB\\n" '

	# Out
	cmd += 'AREA:max_out#ff00ff: '
	cmd += 'AREA:min_out#cc00cc:"Out" '
	cmd += 'LINE1:out#000000 '
	cmd += 'GPRINT:outavg:"%6.2lf %sB" '
	cmd += 'GPRINT:outtot:"%6.2lf %sB" '

	# Diff out
	cmd += 'CDEF:diffout=diff,0,GT,diff,0,IF '
	cmd += 'VDEF:diffouttot=diffout,TOTAL '
	cmd += 'VDEF:diffoutavg=diffout,AVERAGE '
	cmd += 'GPRINT:diffoutavg:"%6.2lf %sB" '
	cmd += 'GPRINT:diffouttot:"%6.2lf %sB\\n" '

	# Sum
	cmd += 'CDEF:sum=in,out,+ '
	cmd += 'VDEF:tot=sum,TOTAL '
	cmd += 'VDEF:avg=sum,AVERAGE '
	cmd += 'LINE1:diff#ffff00:"Sum" '

	cmd += 'GPRINT:avg:"%6.2lf %sB" '
	cmd += 'GPRINT:tot:"%6.2lf %sB" '

	cmd += 'VDEF:difftot=diff,TOTAL '
	cmd += 'VDEF:diffavg=diff,AVERAGE '
	cmd += 'GPRINT:diffavg:"%6.2lf %sB" '
	cmd += 'GPRINT:difftot:"%6.2lf %sB\\n" '

	os.system(cmd)

	#Log network graph
	cmd = 'rrdtool graph '+prefix+'/net-'+interface+'-log.png '+cmd_common
	cmd += '--title "Network traffic: '+interface+'" -o '
	cmd += 'DEF:in=rrd/net-'+interface+'.rrd:in:AVERAGE '
	cmd += 'DEF:out=rrd/net-'+interface+'.rrd:out:AVERAGE '
	cmd += 'DEF:min_in=rrd/net-'+interface+'.rrd:in:MIN '
	cmd += 'DEF:min_out=rrd/net-'+interface+'.rrd:out:MIN '
	cmd += 'DEF:max_in=rrd/net-'+interface+'.rrd:in:MAX '
	cmd += 'DEF:max_out=rrd/net-'+interface+'.rrd:out:MAX '
	cmd += 'CDEF:bi=in,UN,INF,in,IF '
	cmd += 'AREA:bi#DDDDDD: '
	cmd += 'CDEF:bo=out,UN,INF,0,IF '
	cmd += 'AREA:bo#DDDDDD: '

	cmd += 'CDEF:diff=out,in,- '
	cmd += 'VDEF:intot=in,TOTAL '
	cmd += 'VDEF:outtot=out,TOTAL '
	cmd += 'VDEF:inavg=in,AVERAGE '
	cmd += 'VDEF:outavg=out,AVERAGE '

	cmd += 'COMMENT:"      Average       Total     Diff Avg   Diff Tot\\n" '

	# Sum
	cmd += 'CDEF:sum=in,out,+ '
	cmd += 'CDEF:sum_min=min_in,min_out,+ '
	cmd += 'CDEF:sum_max=max_in,max_out,+ '
	cmd += 'VDEF:tot=sum,TOTAL '
	cmd += 'VDEF:avg=sum,AVERAGE '

	cmd += 'AREA:sum#cccc00 '
	cmd += 'AREA:sum#aaaa00:"Sum" '
	cmd += 'LINE1:sum#000000 '

	cmd += 'GPRINT:avg:"%6.2lf %sB" '
	cmd += 'GPRINT:tot:"%6.2lf %sB" '

	cmd += 'VDEF:difftot=diff,TOTAL '
	cmd += 'VDEF:diffavg=diff,AVERAGE '
	cmd += 'GPRINT:diffavg:"%6.2lf %sB" '
	cmd += 'GPRINT:difftot:"%6.2lf %sB\\n" '

	# In
	cmd += 'CDEF:diffin=diff,0,GT,0,diff,-1,*,IF '
	cmd += 'VDEF:diffintot=diffin,TOTAL '
	cmd += 'VDEF:diffinavg=diffin,AVERAGE '
	cmd += 'AREA:diffin#00cccc:"In " '
	cmd += 'GPRINT:inavg:"%6.2lf %sB" '
	cmd += 'GPRINT:intot:"%6.2lf %sB" '
	cmd += 'GPRINT:diffinavg:"%6.2lf %sB" '
	cmd += 'GPRINT:diffintot:"%6.2lf %sB\\n" '

	# Out
	cmd += 'CDEF:diffout=diff,0,GT,diff,0,IF '
	cmd += 'VDEF:diffouttot=diffout,TOTAL '
	cmd += 'VDEF:diffoutavg=diffout,AVERAGE '
	cmd += 'AREA:diffout#cc00cc:"Out" '
	cmd += 'GPRINT:outavg:"%6.2lf %sB" '
	cmd += 'GPRINT:outtot:"%6.2lf %sB" '
	cmd += 'GPRINT:diffoutavg:"%6.2lf %sB" '
	cmd += 'GPRINT:diffouttot:"%6.2lf %sB\\n" '

	# Diff out

	os.system(cmd)


# Process
dirList = os.listdir("rrd/")
for proc in dirList:
	if proc[0:5] != "user-":
		continue
	name = proc.replace(".rrd", "").replace("user-", "")
	print "User: " + name

	#User memory usage
	cmd = 'rrdtool graph '+prefix+'/user-'+name+'-memory.png '+cmd_common
	cmd += '--title "Memory usage: '+name+'" -l0 -M -b 1024 '
	cmd += ' DEF:rss=rrd/'+proc+':rss:AVERAGE'
	cmd += ' DEF:vsz=rrd/'+proc+':vsz:AVERAGE'
	cmd += ' DEF:rss_min=rrd/'+proc+':rss:MIN'
	cmd += ' DEF:vsz_min=rrd/'+proc+':vsz:MIN'
	cmd += ' DEF:rss_max=rrd/'+proc+':rss:MAX'
	cmd += ' DEF:vsz_max=rrd/'+proc+':vsz:MAX'

	cmd += ' CDEF:bo=rss,UN,INF,0,IF'

	cmd += ' AREA:bo#DDDDDD:'

	cmd += ' AREA:vsz_max#ffff00 '
	cmd += ' AREA:vsz_min#cccc00 '
	cmd += ' AREA:rss_max#00ff00 '
	cmd += ' AREA:rss_min#00cc00 '
	cmd += ' LINE1:vsz#888800 '
	cmd += ' LINE1:rss#008800 '

	os.system(cmd)

	#User process usage
	cmd = 'rrdtool graph '+prefix+'/user-'+name+'-cpu.png '+cmd_common
	cmd += '--title "CPU usage: '+name+'" -l0 -M '
	cmd += ' DEF:pcpu=rrd/'+proc+':pcpu:AVERAGE'
	cmd += ' DEF:pcpu_min=rrd/'+proc+':pcpu:MIN'
	cmd += ' DEF:pcpu_max=rrd/'+proc+':pcpu:MAX'

	cmd += ' CDEF:bo=pcpu,UN,INF,0,IF'

	cmd += ' AREA:bo#DDDDDD:'

	cmd += ' AREA:pcpu_max#ffcc00 '
	cmd += ' AREA:pcpu_min#cc9900 '
	cmd += ' LINE1:pcpu#000000 '

	os.system(cmd)

# Disk usage
dirList = os.listdir("rrd/")
for file in dirList:
	if file[0:5] != "disk-":
		continue
	name = file.replace(".rrd", "").replace("disk-", "")
	print "Disk: " + name

	#User memory usage
	cmd = 'rrdtool graph '+prefix+'/disk-'+name+'.png '+cmd_common
	cmd += '--title "Disk usage: '+name+'" -l0 -M -b 1024 '
	cmd += ' DEF:size=rrd/'+file+':size:AVERAGE'
	cmd += ' DEF:used=rrd/'+file+':used:AVERAGE'

	cmd += ' AREA:size#cccccc '
	cmd += ' AREA:used#00ff00 '
	cmd += ' LINE1:used#000000 '

	os.system(cmd)

