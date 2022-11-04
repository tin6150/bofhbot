#!/global/software/sl-7.x86_64/modules/langs/python/3.6/bin/python3

## #!/usr/bin/env python3
## root don't have access SMF

## run as (tin@master): 
## exp: 8 ## pdsh -w n0[143-145,174-176,258-261].savio3 /global/home/users/tin/tin-gh/bofhbot/checkGpuOnNode.py   
## exp: 4 ## pdsh -w n0[134-138,158-161].savio3 /global/home/users/tin/tin-gh/bofhbot/checkGpuOnNode.py   
## exp: 2 ## pdsh -w n0[209-217,262-264].savio3 /global/home/users/tin/tin-gh/bofhbot/checkGpuOnNode.py   
## exp: 2 ## pdsh -w n0[004-005].savio3 /global/home/users/tin/tin-gh/bofhbot/checkGpuOnNode.py   

## version/changes
## 0.1 Tin usable deviceQuery detection 


import socket 
# bothbot_lib mostly for "import os" and the dbg fn
import bofhbot_lib
from bofhbot_lib import *
# could be set by argparse -v, recycle from bofhbot.py ++FIXME++
bofhbot_lib.verboseLevel = 0 #6
bofhbot_lib.dbgLevel = 0 #6

# global param :)  better as OOP get() fn or some such.
devQueryOutFile = '/var/tmp/devQuery.sn50.out' # store deviceQuery output
osDevOutFile = '/var/tmp/osDev.sn60.out'       # store ls -l /dev/nvidia* 


def queryDevicePresent() : 
  # run command /usr/local/bin/deviceQuery  to detect number of live GPU on a system
  # don't seems to need root access to run deviceQuery
  # (lspci | grep NVIDIA does not get smaller when GPU fricks out)
  # deviceQuery | tee /global/scratch/users/tin/pub/devQ.n0144.out | grep Device\ [0-9] 
  # seems to reliably show how many GPU is actually live on the system.
  # ELSE, if result has 
  # Result = FAIL
  # then no gpu was found (eg n0258.savio3 after all gpu not usable, or n0054 which has no GPU)
  devQueryCount = 0
  devPattern = 'Device\ [0-9]'
  command = "/usr/local/bin/deviceQuery" + " > " + devQueryOutFile 
  runDevQueryExitCode = os.system(command) 
  os.chmod(devQueryOutFile, 0o777)  # that strange 0o777 is needed by python
  devQueryFH = open( devQueryOutFile, 'r' )
  for line in devQueryFH : 
    dbg(4, "processing '%s'" % line.rstrip() )
    currentLine = re.search( devPattern, line )  
    if( currentLine ) :
      dbg(5, "found a device line" )
      devQueryCount = devQueryCount + 1
    #enf-if
  #end-for
  dbg(2, "queryDevicePresent() about to return with %s" % devQueryCount )
  return devQueryCount
# queryDevicePresent()-end
  

def queryOsDevPresent() : 
  # count /dev/nvidia0 .. nvidia7 , but may include dead device
  osDevCount = 0
  osDevPattern = '/dev/nvidia[0-9]'
  command = "ls -l %s*" % osDevPattern + " > " + osDevOutFile 
  runQueryOsDevPresentExitCode = os.system(command) 
  os.chmod(osDevOutFile, 0o777)
  osDevFH = open( osDevOutFile, 'r' )
  for line in osDevFH : 
    dbg(4, "processing '%s'" % line.rstrip() )
    currentLine = re.search( osDevPattern, line )  
    if( currentLine ) :
      dbg(5, "found a /dev/nvidia line" )
      osDevCount = osDevCount + 1
    #enf-if
  #end-for
  dbg(2, "queryOsDevPresent() about to return with %s" % osDevCount )
  return osDevCount
# queryOsDevPresent()-end
  

def  findExpectedGpu() :
  # ++FIXME++  stubcode below
  # this function will parse /etc/slurm/gres.conf 
  # use the current hostname ( machineName could be passed as fn argument )
  # return how many gpu this machine should have
  # node that have no gpu should return 0
  return 0  
# findExpectedGpu()-end


def main():
  bofhbot_lib.dbg(5, "bofhbot I am")
  vprint(1, "## checkGpuOnNode.py begin  ##")
  machineName = socket.gethostname()
  devQueryFound = queryDevicePresent()
  gpuExpect = "2,4,8" # need parse gres.conf  # ++FIXME++ findExpectedGpu($machineName)
  osDevCount  = queryOsDevPresent()
  #print( "host: %s ; deviceQuery found: %s ; gpuExpected: %s ; /dev/nvidia* count: %s"  % (machineName, devQueryFound, gpuExpect, osDevCount ) )
  print( "host: %s ; gpuExpected: %s ; /dev/nvidia* count: %s ; deviceQuery found: %s"  % (machineName, gpuExpect, osDevCount, devQueryFound ) )

	# stricly should clean up the /var/tmp/*out files created.  but they are 777 mode for now and maybe useful to have them around.
# main()-end


main()


#### vim modeline , but don't seems to fork on brc login node :(
#### vim: syntax=python
