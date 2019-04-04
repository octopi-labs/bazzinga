
class Sms(object):
    """
    Dove soft message
    """
    def __init__(self, **kwargs):
        """
        Constructs Dove Soft Message object.

        Args:
            mobile: Recipient mobile number
            message: SMS body
            senderid: Sender id [merchant id]
            accusage: Account usage type
            unicode_status: Unicode enabled or not [Optional]
            smstype: type of sms [Optional]
            time: Set date and time [Optional]
            idno: id no [Optional]
        """
        self.mobile = kwargs.get("mobile", "")
        self.message = kwargs.get("message", "")
        self.senderid = kwargs.get("senderid", "")
        self.accusage = kwargs.get("accusage", "")
        self.unicode_status = kwargs.get("unicode_status", "")
        self.smstype = kwargs.get("smstype", "")
        self.time = kwargs.get("time", "")
        self.idno = kwargs.get("idno", "")

    def set_mobile(self, mobile):
        self.mobile = mobile

    def set_message(self, message):
        self.message = message

    def set_senderid(self, senderid):
        self.senderid = senderid

    def set_accusage(self, accusage):
        self.accusage = accusage

    def set_unicode_status(self, unicode_status):
        self.unicode_status = unicode_status

    def set_smstype(self, smstype):
        self.smstype = smstype

    def set_time(self, time):
        self.time = time

    def set_idno(self, idno):
        self.idno = idno
