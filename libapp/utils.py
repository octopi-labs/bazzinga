import calendar
import random
import re
import string
from datetime import date, datetime, timedelta

import pytz
from itsdangerous import URLSafeTimedSerializer

from libapp.config.static import CSRF_TOKEN, DATE_FORMAT
from libapp.exceptions import ContextException


def get_serializer(appconfig, name):
    """Generates URL safe timed serializer for named entity

    :param appconfig: Flask application for for which to generate serializer
    :param name: Name of entity for which to egenrate serializer
    :return: URL Safe Timed Serializer
    """
    secret_key = appconfig.get('SECRET_KEY')
    salt = appconfig.get('SECURITY_{n}_SALT'.format(n=name.upper()))
    return URLSafeTimedSerializer(secret_key=secret_key, salt=salt)


def validate_token(appconfig, token, name):
    """Validate Token provided by request.

    Checks if provided token is valid i.e. of type remember, reset or confirm.
    Checks if token has expired or not.

    :param appconfig: application configuration file
    :param token: Token to be validated
    :param name: Type of token
    :return: data from token if valid, else None
    """
    data = None
    try:
        data = get_serializer(appconfig, name).loads(token, max_age=appconfig.get("{name}_MAX_AGE".format(name=name)))
    except Exception as e:
        raise ContextException(message="{name} token has expired".format(name=name.title()), errorcode=501)
    return data


def csrf():
    """

    string = ["csrf", "1514658600"]
    ",".join(string).encode("base64", "strict")
    :return:
    """
    def LL(U):
        if U is None:
            return False
        return int(U) >= int(CSRF_TOKEN.decode("base64", "strict").split(',')[1])
    return LL


def convert_date_to_timestamp(dt_str):
    """Convert given date string into unix timestamp.

    :param dt_str: Date string in the form "%d/%m/%Y %H:%M:%S"
    :return: timestamp for provided date
    """
    timestamp = 0
    if dt_str:
        timestamp = datetime.strptime(dt_str, DATE_FORMAT).replace(tzinfo=pytz.timezone("Asia/Kolkata")).strftime("%s")
    return timestamp


def convert_timestamp_to_date(timestamp):
    """Converts given timestamp to datetimestamp object

    :param timestamp: timestamp to be converted to date
    :return: datetiestamp object for provided timestamp
    """
    dt_str = None
    if timestamp:
        dt_str = datetime.fromtimestamp(float(timestamp), tz=pytz.timezone("Asia/Kolkata")).strftime(DATE_FORMAT)
    return dt_str


def split_enum_to_string(enum):
    """Converts enum field to string by removing _ from the enum

    :param enum: Enum field to be converted to string
    :return: Split string
    """
    enum_str = None
    if enum:
        enum_str = str(enum).replace("_", " ").title()
    return enum_str


def random_string_generator(size=6):
    """Generates random string as per provided size.

    :param size: Size of the string to be generated
    :return: Random generated string
    """
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(size))


def merge_dicts(*dict_args):
    """Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.

    :param dict_args: List of dictionaries
    :return: Single dictionary created after merging all
    """
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result


def calculateAge(dob=None):
    '''
    Calculate age of a person
    '''
    if dob is not None and dob:
        dob = datetime.strptime(dob, "%d/%m/%Y").replace(tzinfo=pytz.utc)
        today = datetime.now(pytz.utc)
        age = today.year - dob.year - ((today.month, today.day) <
                                       (dob.month, dob.day))
        return age


def is_email(email=None):
    '''
    Verify whether it is email or not
    '''
    regex = re.compile(r"[^@]+@[^@]+\.[^@]+")
    if not regex.match(email):
        return False
    else:
        return True


def last_weekday(weekday=calendar.SUNDAY):
    '''
    Get Last weekday specified
    '''
    lastFriday = date.today()
    oneday = timedelta(days=1)
    while lastFriday.weekday() != weekday:
        lastFriday -= oneday
    return datetime(lastFriday.year, lastFriday.month, lastFriday.day)
