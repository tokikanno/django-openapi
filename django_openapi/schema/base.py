# -*- coding:utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function

from copy import copy
from abc import ABCMeta, abstractmethod
from collections import OrderedDict, Iterable, Mapping

import six

from .fields import BaseSchemaElement
from .fields.utils import is_iterable

_model_to_ref_name_map = {}
_ref_name_to_schema_map = {}


class BaseModel(object):
    def __init__(self, *args, **kwargs):
        processed_key_set = set()

        # load from scdhemas
        for name, field in self.iter_schema_fields():
            value = kwargs.get(name, None)

            position = [name]
            value = field.parse(value, position)

            setattr(self, name, value)
            processed_key_set.add(name)

        # load additionalProperties
        # TODO: add config class for dealing with additional properties
        # TODO: add root class setting
        for k, v in six.iteritems(kwargs):
            if k in processed_key_set:
                continue

            setattr(self, k, v)

    def __to_json_value(self, v):
        if isinstance(v, BaseModel):
            return v.to_json_dict()

        elif isinstance(v, Mapping):
            return {
                _k: self.__to_json_value(_v) for _k, _v in six.iteritems(v)
            }

        elif is_iterable(v):
            return [self.__to_json_value(x) for x in v]

        else:
            return v

    def to_json_dict(self):
        json_d = {}
        for k, v in self.__dict__.items():
            json_d[k] = self.__to_json_value(v)

        return json_d

    @classmethod
    def get_schema_field(cls, name):
        field = getattr(cls, name, None)
        if isinstance(field, BaseSchemaElement):
            return field

        return None

    @classmethod
    def iter_schema_fields(cls):
        for name in dir(cls):
            if name.startswith('__'):
                continue

            value = getattr(cls, name)
            if isinstance(value, BaseSchemaElement):
                yield (name, value)

    @classmethod
    def get_json_schema(cls):
        if cls in _model_to_ref_name_map:
            return _ref_name_to_schema_map[_model_to_ref_name_map[cls]]

        schema_d = {}
        schema_d['type'] = 'object'
        schema_d['properties'] = OrderedDict()
        schema_d['required'] = []

        for name, field in cls.iter_schema_fields():
            schema_d['properties'][name] = field.get_json_schema()
            if field.required:
                schema_d['required'].append(name)

        ref_name = cls.__name__
        if ref_name in _ref_name_to_schema_map:
            ref_name = cls.__module__.replace('.', '_') + '_' + ref_name

        _ref_name_to_schema_map[ref_name] = schema_d
        _model_to_ref_name_map[cls] = ref_name

        return schema_d

    @classmethod
    def get_json_schema_ref(cls):
        if cls in _model_to_ref_name_map:
            return _model_to_ref_name_map[cls]

        cls.get_json_schema()
        return _model_to_ref_name_map[cls]

    @classmethod
    def get_ref_name_to_schema_map(cls):
        return copy(_ref_name_to_schema_map)
