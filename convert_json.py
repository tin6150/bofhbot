#!/usr/bin/env python

import json
import prettytable
import sys

def show_table(j):
   pt = prettytable.PrettyTable()
   c_names = j[list(j.keys())[0]].keys()
   pt.field_names = c_names

   for i in j:
      pt.add_row([j[i][x] for x in j[i].keys()])
   print(pt)

if __name__ == '__main__':
   show_table(json.loads(''.join(sys.stdin.readlines())))
