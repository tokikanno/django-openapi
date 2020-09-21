# -*- coding:utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function

from .base import BaseSchemaElement
from .constants import NO_DEFULAT_VALUE
from .exceptions import SchemaValidationError
from .utils import ensure_set


class NumberField(BaseSchemaElement):
    def __init__(
        self,
        default_value=NO_DEFULAT_VALUE,
        required=True,
        title=None,
        description=None,
        example=None,
        gt=None,
        gte=None,
        lt=None,
        lte=None,
        multiple_of=None,
        enums=None,
    ):
        super(NumberField, self).__init__(
            default_value=default_value,
            required=required,
            title=title,
            description=description,
            example=example,
        )
        self.gt = gt
        self.gte = gte
        self.lt = lt
        self.lte = lte
        self.multiple_of = multiple_of
        if enums:
            self.enums = tuple(enums)
            self.enum_set = set(self.enums)
        else:
            self.enums = None
            self.enum_set = None

    def parse(self, value, position):
        value = super(NumberField, self).parse(value, position)

        if value is None and not self.required:
            return value

        if not isinstance(value, (int, float)):
            try:
                f_value = float(value)
                value = int(value) if f_value.is_integer() else f_value
            except (TypeError, ValueError):
                raise SchemaValidationError(
                    value, 'TYPE_MISMATCH', constraint='number', position=position,
                )

        if self.enums and value not in self.enum_set:
            raise SchemaValidationError(
                value, 'VALUE_NOT_IN_ENUM', constraint=self.enums, position=position,
            )

        if self.gt is not None and not value > self.gt:
            raise SchemaValidationError(
                value, 'VALUE_MUST_GREATER_THAN', constraint=self.gt, position=position,
            )

        if self.gte is not None and not value >= self.gte:
            raise SchemaValidationError(
                value,
                'VALUE_MUST_GREATER_EQUAL_THAN',
                constraint=self.gte,
                position=position,
            )

        if self.lt is not None and not value < self.lt:
            raise SchemaValidationError(
                value, 'VALUE_MUST_LESSER_THAN', constraint=self.lt, position=position,
            )

        if self.lte is not None and not value <= self.lte:
            raise SchemaValidationError(
                value,
                'VALUE_MUST_LESSER_EQUAL_THAN',
                constraint=self.gte,
                position=position,
            )

        if self.multiple_of is not None and value % self.multiple_of != 0:
            raise SchemaValidationError(
                value,
                'VALUE_NOT_MUTLIPLE_OF',
                constraint=self.multiple_of,
                position=position,
            )

        return value

    def get_json_schema(self):
        schema_d = super(NumberField, self).get_json_schema()

        schema_d['type'] = 'number'
        if self.gt is not None:
            schema_d['exclusiveMinimum'] = self.gt
        if self.gte is not None:
            schema_d['minimum'] = self.gte
        if self.lt is not None:
            schema_d['exclusiveMaximum'] = self.lt
        if self.lte is not None:
            schema_d['maximum'] = self.lte
        if self.enums:
            schema_d['enum'] = list(self.enums)

        return schema_d
