#!/global/software/sl-7.x86_64/modules/langs/python/3.6/bin/python

import csv, datetime, os
import smtplib
import getpass
from tools import *
from jinja2 import Environment, FileSystemLoader



def main():
  notest = True
  # Email info.
  server = 'master.brc.berkeley.edu'
  From = 'High Performance Computing Services <hpcs@lbl.gov>'
  Cc = []
  Bcc = ['High Performance Computing Services <hpcs@lbl.gov>']

  # Sends a test email 
  subject = "[BRC GPU error]"
  To = ['hchristopher@lbl.gov']
  Cc = ['tin@lbl.gov']
  Bcc = []
  feeder = ""
  with open(f"/global/home/users/{getpass.getuser()}/bofhbot/data/fullReport.txt", "r") as file_in:
   feeder = file_in.read()
  try:
    if(len(feeder)!=0):
      info('Sending email to \"%s\" ...' % To)
      email = send_email(server, From, To, Cc, Bcc, subject, feeder, notest)
  except:
   error('Error sending email to \"%s\", abort.' % To)


   
if __name__ == '__main__': main()
