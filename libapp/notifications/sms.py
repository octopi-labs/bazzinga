import os

from flask import render_template

from libapp import app, dovesoft
from libapp.config import smsconf
from libapp.dovesoft.exceptions import DoveSoftClientError

from .notifications import Notification

ds = dovesoft.DoveSoftClient(smsconf.USERNAME, smsconf.KEY)


class Sms(Notification):

    def __init__(self, **kwargs):
        super(Sms, self).__init__(**kwargs)

    def get_templates(self, template_name, **kwargs):
        """
        Get text templates for sms
        """
        text = render_template("{template}.txt".format(template=template_name), **kwargs)
        return text

    def get_message(self, **kwargs):
        """
        Get message object for sms
        """
        message = dovesoft.Sms()

        for key in kwargs.keys():
            if key not in kwargs.get("ignore", smsconf.IGNORE_KEYS):
                fun = getattr(message, "set_{key}".format(key=key))
                fun(kwargs.get(key, ""))

        return message

    def send_message(self, message):
        """
        Send message to receiver via gateway
        """
        try:
            resp = ds.send(message)
            app.logger.info("Successfully sent message: {msg}".format(msg=resp))
            return resp
        except DoveSoftClientError as sgce:
            app.logger.error("Error while sending email: {msg}".format(msg=resp))
            app.logger.error("Email: {message}".format(message=message))
            raise DoveSoftClientError(sgce.code, sgce.read())

    def message_notifier(self, **kwargs):
        """
        Message notifier helper to send message
        """
        if all(key in kwargs for key in ["msg_type", "author", "category"]):
            template_name = os.path.join(kwargs.get("msg_type", ""), kwargs.get("author", ""),
                                         kwargs.get("category", ""), kwargs.get("template", ""))
            kwargs = self.del_keys(kwargs.get("delete", smsconf.DELETE_KEYS), **kwargs)
            text = self.get_templates(template_name=template_name, **kwargs)
            message = self.get_message(message=text, **kwargs)
            resp = self.send_message(message)
            app.logger.info("{error} with {res}".format(error=resp[0], res=str(resp[1]).strip("\r\n").rstrip("\n\n")))
        else:
            app.logger.error("No template data available: {data}".format(data=kwargs.keys()))
