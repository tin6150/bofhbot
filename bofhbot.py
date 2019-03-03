#!/usr/bin/env python3

#### module load python/3.6
#### need python3 cuz exception handling for ssh call

# bofhbot - An enhanced sinfo -R for lazy sys admins--aka bofh :)
# see README.rst for detailed description (and license).
# tin (at) berkeley.edu 

# future exercise can likely write this using functional approach
# for now, regular scripting style. 
# OOP can have a structure with problem node as list of objects
# and parallel ssh/ping/etc check on them 
# to speed up output

# most functions moved to bofhbot_lib so that it can be used by the botd api server -Sn 2019.0302

import bofhbot_lib
from bofhbot_lib import *

import argparse


def process_cli() :
        # https://docs.python.org/2/howto/argparse.html#id1
        parser = argparse.ArgumentParser( description='This script give enhanced status of problem nodes reported by eg sinfo -R')
        parser.add_argument('-i', '--ipmi',  help="include ipmi test (may req elevated priv)",  required=False, action="store_true" ) 
        parser.add_argument('-w',  help="TBA pdsh-style list of nodes eg n00[06-17].sav3" ) 
        parser.add_argument('-g',  help="TBA heck take /etc/pdsh/group def file for node list" ) 
        parser.add_argument('-n', '--nodelist',  help="Use a specified nodelist file, eg /etc/pdsh/group/all",  required=False, default="" ) 
        parser.add_argument('--color', help='Color output text', action='store_true')
        parser.add_argument('-s', '--sfile',  help='Use a file containing output of sinfo -N -R -S %E --format="%N %6t %19H %9u %E"', required=False, default="" ) 
        parser.add_argument('-v', '--verboselevel', help="Add verbose output. Up to -vv maybe useful. ", action="count", default=0)
        parser.add_argument('-d', '--debuglevel', help="Debug mode. Up to -ddd useful for troubleshooting input file parsing. -ddddd intended for coder. ", action="count", default=0)
        parser.add_argument('--version', action='version', version='%(prog)s 0.2')
        args = parser.parse_args()
        #-global dbgLevel 
        #-global verboseLevel 
        bofhbot_lib.dbgLevel = args.debuglevel
        bofhbot_lib.verboseLevel = args.verboselevel
        if args.nodelist != '' :
            args.nodelist = re.sub( r'[^A-Za-z0-9/\-_%\. ]+', r'_', args.nodelist )
            vprint(1, "## cli parse for --nodelist, after cleansing, will use: '%s'" % args.nodelist )
        if args.sfile != '' :
            # check path not having things like /foo/bar;rm /etc/passwd
            # the clean list is probably harsher than need to be , but it is a path, not typically convoluted
            vprint(2, "cli parse for --sfile input  '%s'" % args.sfile )
            args.sfile = re.sub( r'[^A-Za-z0-9/\-_%\. ]+', r'_', args.sfile )  # not sure if i really want to allow space...
            vprint(1, "## cli parse for --sfile will use: '%s'" % args.sfile )
        if args.ipmi :
            dbg(3, "-i or --ipmi option was used" )
        return args
# end process_cli() 




def main(): 
    args = process_cli()
    bofhbot_lib.dbg(5, "bofhbot I am")
    vprint(1, "## sinfo enhanced by bofhbot ##")
    # tmp exit
    #return


    # TODO ++ when turn into OOP
    # create as object property/state info
    # where various args could have "side effects"
    # eg, in addition to handling --nodelist as input for list of hosts
    #     also change the format to narrow the column containing host info (since no sinfo -R data)
    if( args.nodelist != "" ) :
        # used --nodelist option, 
        # nodelistFile = args.nodelist
        # --nodelist eg file /etc/pdsh/group/all -- ie, one hostname per line
        dbg(2, "--nodelist arg was %s" % args.nodelist )
        copyfile( args.nodelist, sinfoRSfile )
    elif( args.sfile != "" ) :
        # used --sfile option, 
        dbg(2, "--sfile arg was %s" % args.sfile )
        dbg(2, "sinfoRSfile is %s" % sinfoRSfile )
        # better off having objects.
        # right now it is like a hack, copy user's provided sinfo file into the location 
        # where my script would store the temporary output
        copyfile( args.sfile, sinfoRSfile )
    else :
        generateSinfo()
    #endif 
    # ++ TODO  currently only read sinfoFile for hostname, rest passed as comment
    #    at least when using --nodelist should narrow the column space since no sinfo -R comment avail.
    sinfoList = buildSinfoList() # fn use "OOP/Global" file containing sinfo output


    # tmp exit (for code dev use)
    #return


    # ++ OOP gather all info
    # ++ TODO consider have diff option and invoke alternate fn to format output

    # Pool doesn't work if /dev/shm is disabled
    # Either everyone can write to it, or it is owned by current user
    shm_permissions = os.stat('/dev/shm')
    if oct(shm_permissions.st_mode)[6] == '7' or shm_permissions.st_uid == os.getuid(): 
        pool = Pool(cpu_count())
        map_fn = pool.map
    else:
        print_stderr('/dev/shm is not available... Using single thread mode')
        sys.stderr.flush()
        map_fn = lambda f, x: list(map(f, x))
    nodes = [ (node, line, args.color) for line in sinfoList for node in getNodeList(line) ]
    map_fn(processLine, nodes)
    cleanUp()
# main()-end


main()


#### vim modeline , but don't seems to fork on brc login node :(
#### vim: syntax=python  
