
# from .. import shortnerd


class URLShortner(object):
    """
    URL shortner class to shorten the url given by user
    """
    def __init__(self, uri, key, token):
        self.uri = uri
        self.key = key
        self.token = token

    def shorten(self, url=None):
        """
        Shorten url and send key and token
        """
        if url is not None:
            self.uri = url
            self.key, self.token = shortnerd.insert(url)
        else:
            raise ValueError("Invalid URL, please check it again")

    def bounce_url(self, key):
        """
        Get bounce URL / original url
        """
        if key is not None:
            self.key = key
            self.uri = shortnerd[key]
        else:
            raise ValueError("Invalid key provided, please check it again")

    def delete(self, token):
        """
        Delete url entry from shortner database
        """
        if token is not None:
             shortnerd.revoke(token)
        else:
            raise ValueError("Invalid token provided, please check it again")
