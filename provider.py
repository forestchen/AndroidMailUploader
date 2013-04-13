import android

droid = android.Android()

def getLastSMSByThread(threadID, date):
    result, data, error = droid.queryContent(
    "content://sms",
    ["address", "date"],
    "date <? and thread_id =?",
    [date, threadID],
    "date DESC limit 1")
    return data

def getContactName(contactID):
    result, data, error = droid.queryContent(
    "content://com.android.contacts/data",
    ["data1"],
    "raw_contact_id =? and mimetype_id = 7",
    [contactID],
    None)
    return data[0]["data1"]

def getContactIDByPhone(phoneNumber):
    result, data, error = droid.queryContent(
    "content://com.android.contacts/data",
    ["raw_contact_id"],
    "data1 =? and mimetype_id =5",
    [phoneNumber],
    None)
    return data

def getLatestSMS(date, limit=10000):
    result, data, error = droid.queryContent(
    "content://sms",
    ["address", "person", "body", "type", "date", "thread_id"],
    "date >?",
    [date, ],
    "date asc limit %d" % limit)
    return data

def getContactNameByPhoneNumber(number):
    contactID = getContactIDByPhone(number)
    if not (contactID == []):
        return getContactName(contactID[0]["raw_contact_id"])
    else:
        return ''

