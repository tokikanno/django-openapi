# -*- coding:utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function

from .constants import SCHEMA_ERROR_TYPE_SET


class SchemaValidationError(Exception):
    def __init__(self, value, err_type, constraint=None, position=None):
        self.value = value
        assert err_type in SCHEMA_ERROR_TYPE_SET
        self.err_type = err_type
        self.constraint = constraint
        self.position = position or []

    def __repr__(self):
        return '{}(value={}, err_type={}, constraint={}, position={})'.format(
            self.__class__.__name__,
            repr(self.value),
            repr(self.err_type),
            repr(self.constraint),
            repr(self.position),
        )

    def __str__(self):
        return self.__repr__()
