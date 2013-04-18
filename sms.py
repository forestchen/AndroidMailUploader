#! /usr/bin/env python
# -*- coding: utf-8 -*-

import time
import re

from mailutils import imapMail
import provider

from config import localProfile, domain, smsLimit


def main():
    mail = imapMail()
    mail.login()
    latestTime = mail.getLatestUploadtime()
    if latestTime is None: exit()
    smsList = provider.getLatestSMS(latestTime, smsLimit)

    messages = []
    for sms in smsList:
        message = {}
        message['body'] = sms['body'].encode('utf-8')
        message['date'] = float(sms['date'])/1000
        address = sms['address'].replace(' ', '')[-11:]
        addressOriginal = sms['address'].replace(' ', '')
        if (sms['type'] == "2"):
            """ message sent from local """
            recipient = provider.getContactNameByPhoneNumber(address)
            message['destination'] = [("%s <%s>" % (recipient, addressOriginal)).encode('utf-8'), ]
            message['origin'] = localProfile
            message['subject'] = recipient.encode('utf-8') if not (recipient == '') else addressOriginal

        else:
            """ message received """
            if sms.has_key('person'):
                sender = provider.getContactName(sms['person'])
            else:
                sender = provider.getContactNameByPhoneNumber(address)
            if sender == "":
                _sender = re.findall('[【\[]([^】\]]+)[】\]]$'.decode('utf-8'), sms['body'])
                if len(_sender) != 0: sender = _sender[0]
            message['origin'] = ("%s <%s>" % (sender, addressOriginal)).encode('utf-8')
            message['destination'] = [localProfile, ]
            if sender != '':
                message['subject'] = sender.encode('utf-8')
            else:
                message['subject'] = addressOriginal
        timeStamp = time.strftime("%-d %b %Y", time.localtime(message['date']))
        message['subject'] = message['subject'] + " on %s" % timeStamp
        message['ID'] = "<%s.%s@%s>" % (addressOriginal, sms['date'], domain)
        lastSMS = provider.getLastSMSByThread(sms['thread_id'], sms['date'])
        if not (lastSMS == []):
            lastSMSAddress = lastSMS[0]['address'].replace(' ', '')
            message['In-Reply-To'] = "<%s.%s@%s>" % (lastSMSAddress,lastSMS[0]['date'], domain)
        else:
            message['In-Reply-To'] = ""

        messages.append(message)

    for msg in messages:
        print " %s" % time.ctime(msg['date']), "\033[A"
        mail.uploadMail(msg['origin'], msg['destination'], msg['subject'], msg['date'], msg['body'],
                msg['ID'], msg['In-Reply-To'])

    mail.close()

if __name__ == "__main__":
    main()
