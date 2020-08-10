# -*- coding:utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function

import six

from .base import BaseSchemaElement
from .constants import NO_DEFULAT_VALUE
from .exceptions import SchemaValidationError

from .utils import int_or_none, ensure_set

import re


class StringField(BaseSchemaElement):
    def __init__(
        self,
        default_value=NO_DEFULAT_VALUE,
        required=True,
        title=None,
        description=None,
        example=None,
        str_format=None,
        min_length=None,
        max_length=None,
        regex=None,
        enums=None,
    ):
        super(StringField, self).__init__(
            default_value=default_value,
            required=required,
            title=title,
            description=description,
            example=example,
        )
        self.format = str_format
        self.min_length = int_or_none(min_length)
        self.max_length = int_or_none(max_length)
        self.regex = re.compile(regex) if regex else None
        if enums:
            self.enums = tuple(enums)
            self.enum_set = set(self.enums)
        else:
            self.enums = None
            self.enum_set = None

    def parse(self, value, position):
        value = super(StringField, self).parse(value, position)

        if value is None and not self.required:
            return value

        try:
            value = six.ensure_text(value)
        except:
            raise SchemaValidationError(
                value, 'TYPE_MISMATCH', constraint='string', position=position
            )

        if self.min_length is not None and len(value) < self.min_length:
            raise SchemaValidationError(
                value,
                'TEXT_TOO_SHORT',
                constraint=self.min_length,
                position=position,
            )

        if self.max_length is not None and len(value) > self.max_length:
            raise SchemaValidationError(
                value,
                'TEXT_TOO_LONG',
                constraint=self.max_length,
                position=position,
            )

        if self.enums and value not in self.enum_set:
            raise SchemaValidationError(
                value,
                'VALUE_NOT_IN_ENUM',
                constraint=self.enums,
                position=position,
            )

        if self.regex and not self.regex.match(value):
            raise SchemaValidationError(
                value,
                'REGEX_NOT_MATCH',
                constraint=self.regex.pattern,
                position=position,
            )

        return value

    def get_json_schema(self):
        schema_d = super(StringField, self).get_json_schema()

        schema_d['type'] = 'string'
        if self.min_length is not None:
            schema_d['minLength'] = self.min_length
        if self.max_length is not None:
            schema_d['maxLength'] = self.max_length
        if self.enums:
            schema_d['enum'] = list(self.enums)
        if self.format:
            schema_d['format'] = self.format

        return schema_d
