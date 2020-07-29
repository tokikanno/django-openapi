# -*- coding:utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function

import six
from collections import Iterable

from six import binary_type

_ALL_STRING_LIKE_TYPES = tuple(
    [six.text_type, six.binary_type] + list(six.string_types)
)


def int_or_none(value):
    return value if isinstance(value, int) else None


def ensure_set(values):
    if isinstance(values, _ALL_STRING_LIKE_TYPES):
        return set([values])

    if isinstance(values, Iterable):
        return set(values)


def is_iterable(value):
    return isinstance(value, Iterable) and not isinstance(
        value, _ALL_STRING_LIKE_TYPES
    )

