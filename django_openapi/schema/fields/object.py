# -*- coding:utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import

import sys
from future.utils import raise_
from collections import Mapping

from .base import BaseSchemaElement
from .constants import NO_DEFULAT_VALUE
from .exceptions import SchemaValidationError
from .utils import int_or_none


class ObjectField(BaseSchemaElement):
    def __init__(
        self,
        model_cls,
        default_value=NO_DEFULAT_VALUE,
        required=True,
        title=None,
        description=None,
        example=None,
        # additional_properties=True,
        # min_properties=None,
        # max_properties=None,
    ):
        from ..base import BaseModel

        assert isinstance(model_cls, type) and issubclass(model_cls, BaseModel)

        super(ObjectField, self).__init__(
            default_value=default_value,
            required=required,
            title=title,
            description=description,
            example=example,
        )
        self.model_cls = model_cls
        # self.additional_properties = additional_properties
        # self.min_properties = int_or_none(min_properties)
        # self.max_properties = int_or_none(max_properties)

    def parse(self, value, position):
        value = super(ObjectField, self).parse(value, position)

        if value is None and not self.required:
            return value

        if not isinstance(value, self.model_cls):
            if isinstance(value, Mapping):
                value_dict = value
            else:
                value_dict = {
                    k: getattr(value, k)
                    for k in dir(value)
                    if not k.startswith('_')
                }

            try:
                self.model_cls(**value_dict)
            except SchemaValidationError as e:
                e.position = position + e.position
                raise e

        return value

    def get_json_schema(self):
        schema_d = super(ObjectField, self).get_json_schema()
        schema_d.update(self.model_cls.get_json_schema())
        return schema_d
