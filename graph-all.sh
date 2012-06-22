#!/bin/sh
# This script can be called as a cron-job to updatethe  graphics
# csm is assumed to be located in the root/home directory
# of a user-account of its own.
cd ~
mkdir images
mkdir images/hour
mkdir images/day
mkdir images/week
mkdir images/month
./graph.py 1	0	images/hour
./graph.py 24	0	images/day
./graph.py 168	0	images/week
./graph.py 744	0	images/month
