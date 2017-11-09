"""
	* Author : Nitin Jamadagni
	* USAGE : python scheduleNodeRed.py <OPTION> <nodesInfoFile> <CIRCEOutputFile>
				<OPTION> : START STOP CLNDDEP
"""

'''
Imports section
'''

import sys

if (len(sys.argv) != 4):
	print "usage : python scheduleNodeRed.py <OPTION> <nodesInfoFile> <CIRCEOutputFile> \n     <OPTION> : START/STOP/CLNDDEP"
	sys.exit()

print "assumed configurations :\n1)$HOME/DR/flows file exists with all the required flows on scheduler machine\n2)Each droplet machines have $HOME/DR/script.js\n3)Each droplet has $HOME/DR/flows/\n4)Have dependencies installed"

import paramiko
import os

from multiprocessing import Process



'''
Utility functions section
'''

def readCIRCEOutput(filename):
	taskmap = {}
	with open(filename,'r') as circeout:
		daglines = int(circeout.readline().strip())
		for line in circeout:
			if daglines>0:
				daglines-=1
			else:
				splits = line.strip().split(' ')
				taskmap[splits[0] + ".json"] = splits[1]
	return taskmap

def readNodeInfo(filename):
	nodesinfo = {}
	with open(filename,'r') as nodefile:
		for line in nodefile:
			splits = line.strip().split(' ')
			nodesinfo[splits[0]] = splits[1:]
	return nodesinfo






'''
Main Runners functions
'''



# TODO : other commnadline args shold be accepted for running the node.js script
def connectAndRunScript(task,node):
	nodesinfo = readNodeInfo(sys.argv[2])
	nodeinfo = nodesinfo[node]
	homefolder = os.environ['HOME']

	os.system("scp " + homefolder + "/DR/flows/" + task + " " + nodeinfo[1] + "@" + nodeinfo[0] + ":$HOME/DR/flows/")

	ssh = paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	ssh.connect(nodeinfo[0],username=nodeinfo[1],password=nodeinfo[2])
	print "starting connection with node :" + str(node)

	chan = ssh.get_transport().open_session()
	# TODO : check for open ports first and then check how to run multiple instances on 1 machine
	command = "cd $HOME/DR;forever start script.js $HOME/DR/flows/" + task + " 8000"
	chan.exec_command(command)
	chan.recv_exit_status()
	print "started node-red flow on node :" + node
	print "closing connection with node : "+ node

	ssh.close()



def connectAndStopScript(task,node):
	nodesinfo = readNodeInfo(sys.argv[2])
	nodeinfo = nodesinfo[node]

	ssh = paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	ssh.connect(nodeinfo[0],username=nodeinfo[1],password=nodeinfo[2])
	print "starting connection with node :" + str(node)

	chan = ssh.get_transport().open_session()
	command = "cd $HOME/DR;forever stop script.js;rm $HOME/DR/flows/"+task
	chan.exec_command(command)
	chan.recv_exit_status()
	print "stopped node-red flow on node :" + node
	print "closing connection with node : "+ node

	ssh.close()



def connectAndCleanNodeRedDeployment(node):
	nodesinfo = readNodeInfo(sys.argv[2])
	nodeinfo = nodesinfo[node]

	ssh = paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	ssh.connect(nodeinfo[0],username=nodeinfo[1],password=nodeinfo[2])
	print "starting connection with node :" + str(node)

	chan = ssh.get_transport().open_session()
	command = "rm -rf $HOME/DR/node-red/;mkdir $HOME/DR/node-red"
	chan.exec_command(command)
	chan.recv_exit_status()
	print "cleaned node-red deployment on node :" + node
	print "closing connection with node : "+ node

	ssh.close()



def startJobs():
	jobs = []
	print "\n\n#####STARTING TASKS ON NODES#####"
	for task,node in readCIRCEOutput(sys.argv[3]).iteritems():
		# TODO : remember to accpet other cmdline args
		task = Process(target=connectAndRunScript, args=(task,node,))
		jobs.append(task)
		task.start()

	for job in jobs:
		job.join()
	print "\n\n#####FINISHED STARTING TASKS ON NODES#####"


def stopJobs():
	jobs = []
	print "\n\n#####STOPPING TASKS ON NODES#####"
	for task,node in readCIRCEOutput(sys.argv[3]).iteritems():
		# TODO : remember to accpet other cmdline args
		# TODO : this should be able to stop each task run separately in the future
		task = Process(target=connectAndStopScript, args=(task,node))
		jobs.append(task)
		task.start()

	for job in jobs:
		job.join()
	print "\n\n#####FINISHED STOPPING TASKS ON NODES#####"


def cleanNodeRedDeployments():
	nodesinfo = readNodeInfo(sys.argv[2])
	jobs = []

	print "\n\n#####CLEANING NODERED ON NODES#####"
	for node in nodesinfo.keys():
		task = Process(target=connectAndCleanNodeRedDeployment, args=(node,))
		jobs.append(task)
		task.start()

	for job in jobs:
		job.join()
	print "\n\n#####FINISHED CLEANING NODERED ON NODES#####"








'''
script flow
'''


if sys.argv[1] == "START":
	startJobs()
elif sys.argv[1] == "STOP":
	stopJobs()
elif sys.argv[1] == "CLNDDEP":
	cleanNodeRedDeployments()

