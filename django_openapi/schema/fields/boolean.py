# -*- coding:utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function
import re

import six

from .base import BaseSchemaElement
from .constants import NO_DEFULAT_VALUE
from .exceptions import SchemaValidationError
from .utils import ensure_set


class BooleanField(BaseSchemaElement):
    def __init__(
        self,
        default_value=NO_DEFULAT_VALUE,
        required=True,
        title=None,
        description=None,
        example=None,
    ):
        super(BooleanField, self).__init__(
            default_value=default_value,
            required=required,
            title=title,
            description=description,
            example=example,
        )

    def parse(self, value, position):
        org_value = value = super(BooleanField, self).parse(value, position)

        if value is None and not self.required:
            return value

        if value in (True, False):
            return value

        if isinstance(value, six.integer_types):
            value = six.text_type(value)

        if isinstance(value, six.string_types):
            value = six.ensure_text(value).lower().strip()

            if value in ('true', 'y', 'yes', '1'):
                return True
            elif value in ('false', 'n', 'no', '0'):
                return False

        raise SchemaValidationError(
            org_value,
            'TYPE_MISMATCH',
            constraint='boolean',
            position=position,
        )

    def get_json_schema(self):
        schema_d = super(BooleanField, self).get_json_schema()

        schema_d['type'] = 'boolean'

        return schema_d
