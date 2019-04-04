import os
import json

import sendgrid
from flask import render_template
from sendgrid.helpers.mail import (Category, Content, Email, Mail,
                                   Personalization)

from libapp import app
from libapp.config import emailconf

from .notifications import Notification

os.environ["SENDGRID_API_KEY"] = emailconf.SG_API_KEY
sg = sendgrid.SendGridAPIClient(apikey=emailconf.SG_API_KEY, raise_errors=True, api_key=emailconf.SG_API_KEY)


class EmailNotifications(Notification):

    def __init__(self, **kwargs):
        # self.personalization = None
        super(EmailNotifications, self).__init__(**kwargs)

    def get_templates(self, template_name, **kwargs):
        """
        Get html and text templates for emails
        """
        html = render_template("{template}.html".format(template=template_name), **kwargs)
        text = render_template("{template}.txt".format(template=template_name), **kwargs)
        return html, text

    def create_personalization(self, **kwargs):
        """Build personalization instance from a dict

        :param kwargs: Dictionary containing personalized params
        :return: personalization object
        """
        personalization = Personalization()
        _diff = set(emailconf.PERSONALIZATION_KEYS).intersection(set(kwargs.keys()))
        if _diff:
            for key in _diff:
                item = kwargs.get(key)
                if item:
                    if key in emailconf.EMAIL_KEYS and not isinstance(item, list):
                        item = item.split(',')
                    if isinstance(item, list):
                        for _addr in item:
                            if not isinstance(_addr, Email):
                                _addr = Email(_addr)
                            func = getattr(personalization, "add_{0}".format(key))
                            if func:
                                func(_addr)
                    else:
                        func = getattr(personalization, "{0}".format(key))
                        if func:
                            func(item)

        return personalization

    def get_message(self, **kwargs):
        """
        Get message object for email
        """
        message = Mail()
        if "from_email" in kwargs:
            sender = Email()
            message_content = kwargs.get("message_content", "")
            sender.name = message_content.get("sender", emailconf.DEFAULT_SENDER)
            sender.email = kwargs.get("from_email", emailconf.DEFAULT_SENDER_EMAIL)
            message.from_email = sender
        if "subject" in kwargs:
            message.subject = kwargs.get("subject", "")
        if "text" in kwargs:
            content = Content("text/plain", kwargs.get("text", ""))
            message.add_content(content)
        if "html" in kwargs:
            content = Content("text/html", kwargs.get("html", ""))
            message.add_content(content)
        if "category" in kwargs:
            category = Category(kwargs.get("category", ""))
            message.add_category(category)

        personalization = self.create_personalization(**kwargs)
        if personalization:
            message.add_personalization(personalization)

        return message.get()

    def send_message(self, message):
        """
        Send message to receiver via gateway
        """
        try:
            msg = sg.client.mail.send.post(request_body=message)
            app.logger.info("{error} with {response}".format(error=msg.status_code, response=msg.body))
            app.logger.info("Successfully sent message: {msg}".format(msg=msg))
        except Exception as e:
            app.logger.exception("Error While sending emails: {msg}".format(msg=message))
            app.logger.exception(e)

    def message_notifier(self, **kwargs):
        """
        Message notifier helper to send message
        """
        if all(key in kwargs for key in ["msg_type", "author", "category"]):
            template_name = os.path.join(kwargs.get("msg_type", ""), kwargs.get("author", ""),
                                         kwargs.get("category", ""), kwargs.get("template", ""))
            kwargs = self.del_keys(kwargs.get("delete", emailconf.DELETE_KEYS), **kwargs)
            html, text = self.get_templates(template_name=template_name, **kwargs)
            message = self.get_message(html=html, text=text, **kwargs)
            self.send_message(message)
        else:
            app.logger.error("No template data available: {data}".format(data=kwargs.keys()))
