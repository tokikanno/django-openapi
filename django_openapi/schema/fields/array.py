# -*- coding:utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function

from collections import Iterable

import six

from .base import BaseSchemaElement
from .constants import NO_DEFULAT_VALUE
from .exceptions import SchemaValidationError
from .utils import int_or_none


class ArrayField(BaseSchemaElement):
    def __init__(
        self,
        item_field,
        default_value=NO_DEFULAT_VALUE,
        required=True,
        title=None,
        description=None,
        example=None,
        min_items=None,
        max_items=None,
        check_unique_items=False,
    ):
        super(ArrayField, self).__init__(
            default_value=default_value,
            required=required,
            title=title,
            description=description,
            example=example,
        )

        assert isinstance(item_field, BaseSchemaElement)
        self.item_field = item_field

        self.min_items = int_or_none(min_items)
        self.max_items = int_or_none(max_items)
        self.check_unique_items = check_unique_items

    def parse(self, value, position):
        value = super(ArrayField, self).parse(value, position)

        if value is None and not self.required:
            return value

        if isinstance(value, six.text_type) or not isinstance(value, Iterable):
            raise SchemaValidationError(
                value, 'TYPE_MISMATCH', constraint='array', position=position,
            )

        if self.check_unique_items:
            value_set = set()
            for idx, item in enumerate(value):
                if item in value_set:
                    raise SchemaValidationError(
                        item,
                        'ARRAY_HAS_NON_UNIQUE_ITEM',
                        constraint=None,
                        position=position + [idx],
                    )
                value_set.add(item)

        new_values = []
        for idx, item in enumerate(value):
            new_values.append(self.item_field.parse(item, position + [idx]))

        value = new_values

        if self.min_items is not None and len(value) < self.min_items:
            raise SchemaValidationError(
                value,
                'ARRAY_HAS_TOO_FEW_ITEMS',
                constraint=self.min_items,
                position=position,
            )

        if self.max_items is not None and len(value) > self.max_items:
            raise SchemaValidationError(
                value,
                'ARRAY_HAS_TOO_MANY_ITEMS',
                constraint=self.max_items,
                position=position,
            )

        return value

    def get_json_schema(self):
        schema_d = super(ArrayField, self).get_json_schema()
        schema_d['type'] = 'array'
        schema_d['items'] = self.item_field.get_json_schema()
        if self.min_items is not None:
            schema_d['minItems'] = self.min_items
        if self.max_items is not None:
            schema_d['maxItems'] = self.max_items
        if self.check_unique_items:
            schema_d['uniqueItems'] = True
        return schema_d
