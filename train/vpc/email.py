#!/usr/bin/env python
# -*- coding: utf-8 -*-

import imp
import os
import base64
import sys
from util import check_email_template

import requests

from config import *

def email_credentials(conn):
    """Email all user information and credentials listed in USER_FILE"""

    if not os.environ.get("MAILGUN_KEY") or not os.environ.get("MAILGUN_DOMAIN"):
        print "\nERROR: Required environment variable 'MAILGUN_KEY' or 'MAILGUN_DOMAIN' not set!\n"
        sys.exit()
    else:
        MAILGUN_KEY = check_env('MAILGUN_KEY')
        MAILGUN_DOMAIN = check_env('MAILGUN_DOMAIN')

    check_email_template()

    print 'Emailing user information and credentials ...'

    mail = imp.load_source('mail', EMAIL_TEMPLATE)
    with open(USER_FILE) as file:
        for line in file:
            instances = ''
            username = line.split(',')[0].strip()
            email = line.split(',')[1].strip()

            # instances
            files = [f for f in os.listdir('/host/{0}/users/{1}/'.format(VPC, username)) if f.endswith('.txt')]
            target = open('/host/{0}/users/{1}/instances.txt'.format(VPC, username), 'w')
            target.truncate()

            for textfile in files:
                with open('/host/{0}/users/{1}/{2}'.format(VPC, username, textfile)) as f:
                    instances += f.read()
                    instances += '\n'

            target.write(instances)
            target.close()

            try:
                result = requests.post(
                    "https://api.mailgun.net/v3/{0}/messages".format(MAILGUN_DOMAIN),
                    auth = ("api", MAILGUN_KEY),
                    files = [ ("attachment", open ('/host/{0}/users/{1}/{1}-{0}.pem'.format(VPC, username))),
                              ("attachment", open ('/host/{0}/users/{1}/{1}-{0}.ppk'.format(VPC, username))),
                              ("attachment", open ('/host/{0}/users/{1}/instances.txt'.format(VPC, username))) ],
                    data = { 'from': "{0} <{1}>".format(mail.from_name, mail.from_email),
                             'to': email,
                             'subject': mail.subject,
                             'text': mail.text})

                print "Welcome email sent to: '{0}' <{1}> ...".format(username, email)

            except requests.exceptions.ConnectionError as e:
                print 'An error occurred'
                raise
