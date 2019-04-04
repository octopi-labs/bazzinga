import os

import gcm
from flask import render_template
from gcm.gcm import GCMNotRegisteredException

from libapp import app
from libapp.config import pushconf

from .notifications import Notification

gs = gcm.GCM(pushconf.API_KEY, debug=pushconf.DEBUG)


class Push(Notification):

    def __init__(self, **kwargs):
        super(Push, self).__init__(**kwargs)

    def get_templates(self, template_name, **kwargs):
        """
        Get text templates for push
        """
        text = render_template("{template}.txt".format(template=template_name), **kwargs)
        return text

    def get_message(self, **kwargs):
        """
        Get message object for push
        """
        gcm_keys = ["registration_id", "registration_ids", "topic", "retries"]
        message = {}
        message['data'] = {}

        for key in kwargs.keys():
            if key not in kwargs.get("ignore", pushconf.IGNORE_KEYS):
                if key in gcm_keys and kwargs.get(key, None) is not None:
                    message[key] = kwargs.get(key, "")
                elif kwargs.get(key, None) is not None:
                    message['data'].update({key: kwargs.get(key, "")})
                else:
                    # Not sure what to do ;)
                    pass
            elif key == 'message_content':
                msg_content = kwargs.get(key, None)
                for msg_key in msg_content:
                    message['data'].update({msg_key: msg_content.get(msg_key, "")})

        return message

    def send_message(self, message):
        """
        Send message to receiver via gateway
        """
        resp = None
        try:
            if "registration_id" in message:
                resp = gs.plaintext_request(**message)
            elif "registration_ids" in message:
                resp = gs.send_downstream_message(**message)
            else:
                resp = gs.send_topic_message(**message)
        except GCMNotRegisteredException as e:
            app.logger.error("exception: {error}".format(error=e))
            if "registration_id" in message:
                app.logger.error("Registration Id: {error}".format(error=message.get("registration_id", None)))
            elif "registration_ids" in message:
                app.logger.error("Registration Ids: {error}".format(error=message.get("registration_ids", None)))
            else:
                app.logger.error("Topic: {error}".format(error=message.get("topic", None)))
        except:
            app.logger.exception('Got exception while sending message')
            raise
        return resp

    def message_notifier(self, **kwargs):
        """
        Message notifier helper to send message
        """
        if all(key in kwargs for key in ["msg_type", "author", "category"]):
            template_name = os.path.join(kwargs.get("msg_type", ""), kwargs.get("author", ""),
                                         kwargs.get("category", ""), kwargs.get("template", ""))
            kwargs = self.del_keys(kwargs.get("delete", pushconf.DELETE_KEYS), **kwargs)
            text = self.get_templates(template_name=template_name, **kwargs)
            message = self.get_message(text=text, **kwargs)
            resp = self.send_message(message)
            app.logger.info("response with {error}".format(error=resp))
        else:
            app.logger.error("No template data available: {data}".format(data=kwargs.keys()))
