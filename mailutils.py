#!/usr/bin/env python

import imaplib
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate, parsedate_tz, mktime_tz
import time

from config import imapServer, mailUser, mailPassword, mailBoxLabel, markAsRead


class imapMail():


    def __init__(self):
        pass

    def login(self):
        self.mail=imaplib.IMAP4_SSL(imapServer)
        self.mail.login(mailUser, mailPassword)

    def getLatestUploadtime(self):
        result, mailCount = self.mail.select(mailBoxLabel)
        if result == 'OK':
            pass
        elif result == 'NO' and mailCount[0][0:13] == '[NONEXISTENT]':
            result, status = self.mail.create(mailBoxLabel)
            if result != 'OK':
                print "mailbox can not be created."
                return None
            else:
                print "mailbox created"
                self.mail.select(mailBoxLabel)
                mailCount = ['0']
        else:
            print mailCount
            return None

        if mailCount == ['0']: return 0

        msgUIDs = ['']
        """ initial search time within 1 day """
        expandTime = 86400
        while (msgUIDs == ['']):
            """ check for the maximum time """
            if expandTime > 88473600:
                return (time.time() - expandTime)
            sinceTime = imaplib.Time2Internaldate(time.time() - expandTime)
            result, msgUIDs = self.mail.search(None, 'SINCE', sinceTime)
            expandTime = expandTime * 2

        idString = ','.join(msgUIDs[0].split())
        result, msgIDs = self.mail.fetch(idString, '(BODY[HEADER.FIELDS (MESSAGE-ID)])')
        latest = 0
        for msgID in msgIDs:
            if len(msgID) < 2: continue
            try:
                epoch = msgID[1].split('.')[1][0:13]
            except:
                latest = -1
                break
            if epoch > latest:
                latest = epoch

        if latest == -1:
            print "unrecognized message id"
            result, msgDate = self.mail.fetch(idString, '(INTERNALDATE)')
            latest = 0
            for date in msgDate:
                _date = date.split('"')[1]
                seconds = mktime_tz(parsedate_tz(_date))
                if seconds > latest:
                    latest = seconds
            latest = latest * 1000

        return latest

    def uploadMail(self, origin, destination, subject, date, body, ID, inReplyTo, flag=markAsRead):

        mailFlag = ''
        if flag is True:
            mailFlag += '\\SEEN'
        elif type(flag) == type('str'):
            mailFlag += flag

        message = MIMEText(body, 'plain')
        message['From'] = origin
        message['To'] = COMMASPACE.join(destination)
        message['Date'] = formatdate(date, localtime=True)
        message['Subject'] = subject
        message['Message-ID'] = ID
        if inReplyTo != "":
            message['In-Reply-To'] = inReplyTo
            message['References'] = inReplyTo

        self.mail.append(mailBoxLabel,
                mailFlag,
                imaplib.Time2Internaldate(date),
                message.as_string())

    def close(self):
        self.mail.close()
        self.mail.logout()
