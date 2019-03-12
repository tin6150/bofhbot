
# bofhbot api server daemon 
# example use:
# python botd.py -s dev_aid/sample_input/sinfo-RSE.test.txt -ddd -v 

# flask main executable
# run as (with python3 in venv): 
# python botd.py 


from flask import Flask
from flask_restful import Resource, Api
import os
import bofhbot_lib
from   bofhbot_lib import *
import argparse
import re # regular expression


## class wide variables
sinfoGenerationTime = 0     # store a timestamp of when sinfo-RSE was collected (it not using -s)



def process_cli() :
        # https://docs.python.org/2/howto/argparse.html#id1
        parser = argparse.ArgumentParser( description='bofhbot backend api server daemon')
        parser.add_argument('-s', '--sfile',  help='Use a file containing output of sinfo -N -R -S %E --format="%N %6t %19H %9u %E"', required=False, default="" ) 
        parser.add_argument('-v', '--verboselevel', help="Add verbose output. Up to -vv maybe useful. ", action="count", default=0)
        parser.add_argument('-d', '--debuglevel', help="Debug mode. Up to -ddd useful for troubleshooting input file parsing. -ddddd intended for coder. ", action="count", default=0)
        parser.add_argument('--version', action='version', version='%(prog)s 0.1')
        args = parser.parse_args()
        bofhbot_lib.dbgLevel = args.debuglevel
        bofhbot_lib.verboseLevel = args.verboselevel
        if args.sfile != '' :
            # check path not having things like /foo/bar;rm /etc/passwd
            # the clean list is probably harsher than need to be , but it is a path, not typically convoluted
            vprint(2, "cli parse for --sfile input  '%s'" % args.sfile )
            args.sfile = re.sub( r'[^A-Za-z0-9/\-_%\. ]+', r'_', args.sfile )  # not sure if i really want to allow space...
            vprint(1, "## cli parse for --sfile will use: '%s'" % args.sfile )
        return args
# end process_cli() 



app = Flask(__name__)
api = Api(app)

class botD_hello(Resource):
    def get(self):
        return {'bot': 'bofh'}
    def post(self, post_body):
        return {'botD_hello__post': 'not implemented' }
# botD_hello class end ##################################################################
      
class botD_status(Resource):
    def get(self):
        # get status.  for sinfo -RSE (default and only option for now)
        
        # finding source for host list, for now it is whether to run sinfo -RSE
        if( args.sfile != "" ) :
            # used --sfile option, 
            dbg(2, "--sfile arg was %s" % args.sfile )
            dbg(2, "sinfoRSfile is %s" % sinfoRSfile )
            # better off having objects.
            # right now it is like a hack, copy user's provided sinfo file into the location 
            # where my script would store the temporary output
            copyfile( args.sfile, sinfoRSfile )
        else :
            dbg( 1, "calling generateSinfo() , need to be in a slurm cluster to work correctly.")
            generateSinfo()
        #end-if
        
        sinfoList = buildSinfoList() # fn use "OOP/Global" file containing sinfo output

        shm_permissions = os.stat('/dev/shm')
        if oct(shm_permissions.st_mode)[6] == '7' or shm_permissions.st_uid == os.getuid():
            pool = Pool(cpu_count())
            map_fn = pool.map
        else:
            print_stderr('/dev/shm is not available... Using single thread mode')
            sys.stderr.flush()
            map_fn = lambda f, x: list(map(f, x))

        ## ++ continue here FIXME
        useColor = False;
        ## nick did some double for to get the node in single line
        #nodeList = [ (node, line, args.color) for line in sinfoList for node in getNodeList(line) ]
        #nodeList = [ (node, line, useColor) for line in sinfoList for node in getNodeList(line) ]
        # so nodeList above is a list of hostname ?   Not really, they are sinfo-RSE output lines...

        #dbg( 2, sinfoList )  ## dbg
        nodeList  = sinfoList2nodeList( sinfoList )   # this take whole file?   yes but get a list of list ... 
        #nodeList  = getNodeList( sinfoList )   # problem here, getNodeList is badly named...  it takes only one node
# 
        dbg( 2, nodeList )   

        #+ map_fn(processLine, nodeList)   ## this is place of main work and need to be redone for REST/json ++ 
        cleanUp()


        return {'botD_sinfo': 'tba'}   # tmp code
    # get()-end
# botD_status class end ##################################################################

api.add_resource(botD_hello, '/hello')
api.add_resource(botD_status, '/', '/api/v1/status')   # ie respond to two URL.  eventually need to parse status?group=sinfo vs status?group=lr6

if __name__ == '__main__':
    args = process_cli()
    
    dbg(3, "before app.run(), performing some setup")
    status = 0
    #status = generateSinfo()     # this save info in a file, skipping generation for now and use a saved file.
    if status != 0 :
        sinfoGenerationTime = 1 # find out how python can check regenerate only after 5 min
    
    
    #app.run(debug=True)
    port = int(os.environ.get('PORT', 5000))
    #app.run(port=port)                                 # this is default, localhost only    
    #app.run(host='0.0.0.0', port=port, debug=True)      # i have iptables limiting exposure
    app.run(host='0.0.0.0', port=port, debug=args.debuglevel)      # i have iptables limiting exposure
    
    dbg(3, "after app.run(), doing clean up")
    # rm sinfo file
    #+ cleanUp()
    

# vim:shiftwidth=2 tabstop=4 formatoptions-=cro list nu expandtab filetype=python
