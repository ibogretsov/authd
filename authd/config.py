# -*- coding:utf-8 -*-
"""Configuration schema definition.
"""
import datetime
import json

from voluptuous import All
from voluptuous import CoerceInvalid
from voluptuous import Required
from voluptuous import Schema


class TimeSpan(object):
    """Volopuous string to datetime.timedelta converter.
    """

    def __init__(self, format=None, msg=None):
        self.msg = msg
        self.format = format or "%H:%M:%S"

    def __call__(self, value):
        try:
            duration = datetime.datetime.strptime(value, self.format)
            return datetime.timedelta(
                hours=duration.hour,
                minutes=duration.minute,
                seconds=duration.second)
        except (TypeError, ValueError):
            errormsg = self.msg or "unable to parse datetime {0}".format(value)
            raise CoerceInvalid(errormsg)


CONFIG = Schema({
    Required("database"):
    All(Schema({
        Required("DSN"): All(str)
    })),
    Required("security"):
    All(Schema({
        Required("ttl"): All(TimeSpan()),
        Required("key"): All(str)
    }))
})


def load(config_filename):
    with open(config_filename, mode="r", encoding="utf-8") as cfg:
        config = json.load(cfg)
    return CONFIG(config)
