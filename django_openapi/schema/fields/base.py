# -*- coding:utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function

from abc import ABCMeta, abstractmethod

import six

from .constants import NO_DEFULAT_VALUE
from .exceptions import SchemaValidationError


class BaseSchemaElement(six.with_metaclass(ABCMeta, object)):
    @abstractmethod
    def __init__(
        self,
        default_value=NO_DEFULAT_VALUE,
        required=True,
        title=None,
        description=None,
        example=None,
    ):
        self.default_value = default_value
        self.required = required
        self.title = title
        self.description = description
        self.example = example

    @abstractmethod
    def parse(self, value, position):  # list of position info passed by caller
        if value is None:
            if self.default_value is not NO_DEFULAT_VALUE:
                value = self.default_value

        if value is None and self.required:
            raise SchemaValidationError(
                value, 'FIELD_IS_REQUIRED', position=position
            )

        return value

    @abstractmethod
    def get_json_schema(self):
        schema_d = {}
        if self.title:
            schema_d['title'] = self.title
        if self.description:
            schema_d['description'] = self.description
        if self.example:
            schema_d['examples'] = [self.example]
        if self.default_value is not NO_DEFULAT_VALUE:
            schema_d['default'] = self.default_value

        return schema_d

    # @abstractmethod
    # def get_value(self):
    #     pass

    # @abstractmethod
    # def get_json_value(self):
    #     pass
