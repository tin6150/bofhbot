#!/global/software/sl-7.x86_64/modules/langs/python/3.6/bin/python

import csv, datetime, os
import smtplib
import getpass
from tools import *
from jinja2 import Environment, FileSystemLoader

# global parameters: file path to final report
FULL_REPORT = f"/global/home/users/{getpass.getuser()}/bofhbot/data/fullReport.txt"

# this script takes the final report and emails it to henry and tin
def main():
  cluster = os.popen('sacctmgr list cluster | tail -1 | awk \'{print $1;}\'').read().split('\n')[0]
  notest = True
  # Email info.
  # depending on cluster, email is sent through different servers. Subject is also changed to reflect cluster
  if(cluster == 'brc'):
    server = 'master.brc.berkeley.edu'
    subject = "[BRC GPU error]"
  elif(cluster == 'perceus-00'):
    server = 'smtp.lbl.gov'
    subject = "[LRC GPU error]"
  else:
    exit(1)
  From = 'High Performance Computing Services <hpcs@lbl.gov>'
  Cc = []
  Bcc = ['High Performance Computing Services <hpcs@lbl.gov>']

  # Sends a test email 
  To = ['hchristopher@lbl.gov']
  Cc = ['tin@lbl.gov']
  Bcc = []
  feeder = ""
  with open(FULL_REPORT, "r") as file_in:
   feeder = file_in.read()
  try:
    if(len(feeder)!=0):
      info('Sending email to \"%s\" ...' % To)
      email = send_email(server, From, To, Cc, Bcc, subject, feeder, notest)
  except:
   error('Error sending email to \"%s\", abort.' % To)


   
if __name__ == '__main__': main()
