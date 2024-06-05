#!/usr/bin/python2.6
#
# Copyright (c) 2010-2013, Yong Qin <yong.qin@lbl.gov>. All rights reserved.
#

import inspect
import logging
import os
import smtplib
import subprocess
import sys
#from email.MIMEText import MIMEText
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


myname = sys.argv[0]
#logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

def me():
  """
  Return current function name from stack
  Input:  None
  Output: string
  """
  return inspect.stack()[1][3]


def me_lineno():
  """
  Return current line number from stack
  Input:  None
  Output: string
  """
  return inspect.stack()[1][2]


def me_file():
  """
  Return current file from stack
  Input:  None
  Output: string
  """
  return inspect.stack()[1][1].split('/')[-1]



def caller():
  """
  Return caller's function name from stack
  Input:  None
  Output: string
  """
  return inspect.stack()[2][3]


def caller_lineno():
  """
  Return caller's line number from stack
  Input:  None
  Output: string
  """
  return inspect.stack()[2][2]


def caller_file():
  """
  Return caller's file from stack
  Input: None
  Output: string
  """
  return inspect.stack()[2][1].split('/')[-1]


def critical(message, errcode=-1, logger=None):
  """
  Print critical error message and exit with error code
  Input:  string
  Output: None
  """
  message = '(%s->%s->%s(): %s): %s' % (myname, caller_file(), caller(), caller_lineno(), message)
  if logger:
    logger.critical(message)
  else:
    #print >> sys.stderr, 'CRITICAL: %s' % message
    logging.critical(message)
  sys.exit(errcode)


def error(message, errcode=-1, logger=None):
  """
  Print error message and exit with error code
  Input:  string
  Output: None
  """
  message = '(%s->%s->%s(): %s): %s' % (myname, caller_file(), caller(), caller_lineno(), message)
  if logger:
    logger.error(message)
  else:
    #print >> sys.stderr, 'ERROR: %s' % message
    logging.error(message)
  sys.exit(errcode)


def warning(message, logger=None):
  """
  Print warning message
  Input:  string
  Output: None
  """
  message = '(%s->%s->%s(): %s): %s' % (myname, caller_file(), caller(), caller_lineno(), message)
  if logger:
    logger.warning(message)
  else:
    #print >> sys.stderr, 'WARNING: %s' % message
    logging.warning(message)


def debug(message, logger=None):
  """ 
  Print debug message
  Input: string
  Output: None
  """
  message = '(%s->%s->%s(): %s): %s' % (myname, caller_file(), caller(), caller_lineno(), message)
  if logger:
    logger.debug(message)
  else:
    #print >> sys.stderr, 'DEBUG: %s' % message
    logging.debug(message)


def info(message, logger=None):
  """
  Print info or verbose message
  Input: string
  Output: None
  """
  message = '(%s->%s->%s(): %s): %s' % (myname, caller_file(), caller(), caller_lineno(), message)
  if logger:
    logger.info(message)
  else:
    #print >> sys.stderr, 'INFO: %s' % message
    logging.info(message)


def cpu_number():
  """
  Obtain the number of cores/cpus from a system
  Input: None
  Output: int
  """
  try:
    cpu = int(os.sysconf('SC_NPROCESSORS_ONLN'))
    if cpu > 0:
      return cpu
    else:
      return 0
  except (AttributeError, ValueError):
    return 0


def assert_file(file):
  """
  Assert if FILE does not exist
  Input: string
  Output: None
  """
  if not os.path.isfile(file):
    raise_(RuntimeError, 'Can not find file \"%s\"' % file)


def assert_dir(dir):
  """
  Assert if DIR does not exist
  Input: string
  Output: None
  """
  if not os.path.isdir(dir):
    raise_(RuntimeError, 'Can not find directory \"%s\"' % dir)


def read_file(file):
  """
  Read lines from FILE in a whole
  Input: string
  Output: string
  """
  lines = ''
  assert_file(file)
  try:
    out = open(file)
    lines = out.read()
    out.close()
  except:
    raise_(RuntimeError, 'Failed to read from \"%s\"' % file)
  return lines


def write_file(file, lines):
  """
  Write a string to a file
  Input: string, string
  Output: None
  """
  try:
    out = open(file, "w")
    out.write(lines)
    out.close()
  except:
    raise_(RuntimeError, 'Failed to write to \"%s\"' % file)


def uniq_list(seq):
  """
  Obtain the unique elements from a list
  Input: list
  Output: list
  """
  keys = {}
  for each in seq:
    keys[each] = 1
  return keys.keys()


def run_cmd(cmd):
  """
  Run cmd in subprocess, capture outputs and return
  Input: string
  Output: dictionary
  """
  retvalue = {}
  try:
    p = subprocess.Popen(cmd, shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
  except OSError as exc:
    exc.args = ['Can not run \"%s\"']
    raise
  retvalue['retstr'] = p.stdout.read()
  retvalue['retval'] = p.wait()
  return retvalue


def sort_dict_by_key(dict, reverse=False):
  """
  Sort dictionary by keys, return list of tuples
  Input: dictionary, bool
  Output: list of tuples
  """
  return [ (key,dict[key]) for key in sorted(dict.keys(), reverse=reverse) ]


def sort_dict_by_value(dict, reverse=False):
  """
  Sort dictionary by values, return list of tuples
  Input: dictionary, bool
  Output: list of tuples
  """
  items=dict.items()
  backitems=[ [v[1],v[0]] for v in items ]
  backitems.sort(reverse=reverse)
  return [ (backitems[i][1], backitems[i][0]) for i in range(0,len(backitems)) ]


def html_print_h1(title):
  """
  Print HTML H1
  Input: string
  Output: string
  """
  return '    <h1>%s</h1>\n' % title


def html_print_h2(title):
  """
  Print HTML H2
  Input: string
  Output: string
  """
  return '    <h2>%s</h2>\n' % title


def html_print_h3(title):
  """
  Print HTML H3
  Input: string
  Output: string
  """
  return '    <h3>%s</h3>\n' % title


def html_print_bold(title):
  """
  Print HTML Bold
  Input: string
  Output: string
  """
  return '<b>%s</b>' % title


def html_print_italic(title):
  """
  Print HTML Italic
  Input: string
  Output: string
  """
  return '<i>%s</i>' % title


def html_print_divider():
  """
  Print HTML divider
  Input: None
  Output: string
  """
  return '    <hr>\n'


def html_print_break():
  """
  Print HTML line break
  Input: None
  Output: string
  """
  return '<br>'


def html_print_href(title, src):
  """
  Print HTML href
  Input: string, string
  Output: string
  """
  return '<a href=\"%s\">%s</a>' % (src, title)


def html_print_anchor(title, src):
  """
  Print HTML anchor
  Input: string, string
  Output: string
  """
  return '<a name=\"%s\">%s</a>' % (src, title)


def html_print_img(src, alt):
  """
  Print HTML img
  Input: string, string
  Output: string
  """
  return '<img src=\"%s\" alt=\"%s\">' % (src, alt)


def html_print_table_header(row=None, tooltips=None, indent=4*' ', align='center', border='1', width='90%', sorttable=True):
  """
  Print HTML Table header
  Input: list, string, string, string
  Output: string
  """
  if not row:
    return '%s<table border="%s" width="%s">\n' % (indent, border, width)

  if tooltips:
    if len(row) != len(tooltips):
      tooltips = None

  line = ''
  if not sorttable:
    line += '%s<table border="%s" width="%s">\n' % (indent, border, width)
  else:
    line += '%s<table class="sortable" border="%s" width="%s">\n' % (indent, border, width)
  line += indent + '<tr>'
  for i in range(len(row)):
    col = row[i]
    if tooltips:
      tooltip = tooltips[i]
    else:
      tooltip = None

    if col is None:
      line += '<th align="%s">&nbsp;</th>' % (align)
    else:
      if tooltip is None:
        line += '<th align="%s">%s</th>' % (align, col)
      else:
        line += '<th align="%s"><a title="%s">%s</a></th>' % (align, tooltip, col)
  line += '</tr>\n'
  return line


def html_print_table_footer(indent=4*' '):
  """
  Print HTML Table footer
  Input: None
  Output: string
  """
  return indent + '</table>\n'


def html_print_table_row(row=None, indent=6*' ', align='left', highlight=False):
  """
  Print HTML Table row
  Input: list, string, bool
  Output: string
  """
  # use the css highlight style
  if highlight:
    line = indent + '<tr style="background-color: default" onMouseOver="this.className=\'highlight\'" onMouseOut="this.className=\'normal\'">'
  else:
    line = indent + '<tr>'
  for col in row:
    if col is None:
      line += '<td align="%s">&nbsp;</td>' % (align)
    else:
      line += '<td align="%s">%s</td>' % (align, col)
  line += '</tr>\n'
  return line


def html_print_header(title):
  """
  Print HTML header
  Input: string
  Output: string
  """
  line = ''
  line += '<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">\n'
  line += '<html>\n'
  line += '  <head>\n'
  line += '    <meta http-equiv=Content-Type content="text/html; charset=windows-1252">\n'
  line += '    <style type="text/css">\n'
  # highlight the table row
  line += '      .normal    { background-color: default; }\n'
  line += '      .highlight { background-color: lightblue; cursor: default; }\n'
  # highlight the sortable table header
  line += '      table.sortable thead {\n'
  line += '        background-color: lightyellow;\n'
  line += '        color: default;\n'
  line += '        font-weitht: bold;\n'
  line += '        cursor: default;\n'
  line += '      }\n'
  line += '    </style>\n'
  # sortable table header script
  line += '    <script type="text/javascript" src="/sorttable.js"></script>\n'
  line += '    <title>%s</title>\n' % title
  line += '  </head>\n'
  line += '  <body lang=EN-US link=blue vlink=purple style="tab-interval:.5in">\n'
  return line


def html_print_footer():
  """
  Print HTML footer
  Input: None
  Output: string
  """
  line = ''
  line += '    Copyright &copy; 2010 Yong Qin. All rights reserved.\n'
  line += '  </body>\n'
  line += '</html>\n'
  return line


def send_email(server, From, To, Cc, Bcc, subject, content, notest=False):
    """
    Send an email to receiver
    """
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From']    = From
    msg['To']      = ','.join(To)
    msg['Cc']      = ','.join(Cc)
    msg.attach(MIMEText(content, "plain"))

    if notest:
        s = smtplib.SMTP(server)
        s.sendmail(From, To+Cc+Bcc, msg.as_string())
        s.quit()
        email = ''
    else:
        email = msg.as_string()

    return email

def send_html_email(server, From, To, Cc, Bcc, subject, content, notest=False):
    """
    Send an email to receiver
    """
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From']    = From
    msg['To']      = ','.join(To)
    msg['Cc']      = ','.join(Cc)
    msg.attach(MIMEText(content, "html"))

    if notest:
        s = smtplib.SMTP(server)
        s.sendmail(From, To+Cc+Bcc, msg.as_string())
        s.quit()
        email = ''
    else:
        email = msg.as_string()

    return email
