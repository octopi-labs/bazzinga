

class Notification(object):

    def __init__(self):
        """
        Notification
        """
        pass

    def get_templates(self, template_name, **kwargs):
        """
        Abstract function to get all the message templates
        """
        pass

    def get_message(self, **kwargs):
        """
        Abstract function to get all the messages
        """
        pass

    def send_message(self, message):
        """
        Abstract function to send messages
        """
        pass

    def message_notifier(self, **kwargs):
        """
        Abstract function to notify messages
        """
        pass

    def del_keys(self, keys, **kwargs):
        """
        Function to delete unneeded keys
        """
        if not isinstance(keys, list):
            keys = str(keys).split(",")
        for key in keys:
            del kwargs[str(key).strip()]
        return kwargs
