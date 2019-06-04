#!/usr/bin/env python

import json
import prettytable
import sys

def main():
   j = json.load(open(sys.argv[1]))
   pt = prettytable.PrettyTable()
   c_names = j[list(j.keys())[0]].keys()
   pt.field_names = c_names

   for i in j:
      pt.add_row([j[i][x] for x in j[i].keys()])
      #print i, ' | '.join(["%s:%s" % (x, j[i][x]) for x in j[i].keys()])
   print(pt)

if __name__ == '__main__':

   main()
