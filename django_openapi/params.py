# -*- coding:utf8 -*-
from __future__ import unicode_literals
from __future__ import print_function

from abc import ABCMeta, abstractmethod

import six
import json

from django.core.files.uploadedfile import UploadedFile

from .schema.fields import BaseSchemaElement, StringField
from .schema import BaseModel
from .schema.fields.exceptions import SchemaValidationError

_NOT_SET = object()


class BaseRequestParam(six.with_metaclass(ABCMeta, object)):
    IN_POS = _NOT_SET

    @abstractmethod
    def __init__(self):
        assert self.IN_POS is not _NOT_SET

    @abstractmethod
    def get_openapi_schema(self, name):
        pass

    @abstractmethod
    def get_value_from_request(self, request, name):
        pass

    @abstractmethod
    def parse(self, request, name):
        pass


class BaseRequestField(BaseRequestParam):
    def __init__(self, field=None):
        super(BaseRequestField, self).__init__()
        field = field or StringField()

        assert isinstance(field, BaseSchemaElement)
        self.field = field

    def get_openapi_schema(self, name):
        field_schema_d = self.field.get_json_schema()
        description_segs = [
            field_schema_d.pop(k)
            for k in ('title', 'description')
            if field_schema_d.get(k)
        ]

        schema_d = {
            'name': name,
            'required': self.field.required,
            'schema': self.field.get_json_schema(),
            'in': self.IN_POS,
        }

        if description_segs:
            schema_d['description'] = '\n'.join(description_segs)

        return schema_d

    def parse(self, request, name):
        return self.field.parse(
            self.get_value_from_request(request, name), [self.IN_POS, name]
        )


class BaseRequestBodyModel(BaseRequestParam):
    def __init__(self, model_cls):
        assert isinstance(model_cls, type) and issubclass(model_cls, BaseModel)
        self.model_cls = model_cls

    def get_openapi_schema(self):
        schema_d = {
            'content': {
                'application/json': {
                    'schema': {
                        '$ref': '#/components/schemas/'
                        + self.model_cls.get_json_schema_ref()
                    }
                }
            },
            'required': True,
        }

        return schema_d

    def parse(self, request, name):
        try:
            return self.model_cls(**self.get_value_from_request(request, name))
        except SchemaValidationError as e:
            e.position = [self.IN_POS, name] + e.position
            raise e


class Body(BaseRequestBodyModel):
    IN_POS = 'body'

    def get_value_from_request(self, request, name):
        return json.loads(six.ensure_text(request.body))


class Query(BaseRequestField):
    IN_POS = 'query'

    def get_value_from_request(self, request, name):
        return request.GET.get(name)


class Path(BaseRequestField):
    IN_POS = 'path'

    def get_value_from_request(self, request, name):
        return request.path_kwargs.get(name)


class Header(BaseRequestField):
    IN_POS = 'header'

    def get_value_from_request(self, request, name):
        return request.META.get(name.upper())


class Cookie(BaseRequestField):
    IN_POS = 'cookie'

    def get_value_from_request(self, request, name):
        return request.COOKIES.get(name)


class Form(BaseRequestField):
    IN_POS = 'form'

    def get_value_from_request(self, request, name):
        return request.POST.get(name)


class UploadFile(BaseRequestField):
    IN_POS = 'form'

    def __init__(self):
        super(UploadFile, self).__init__(
            StringField(title='Upload file', str_format='binary')
        )

    def get_value_from_request(self, request, name):
        return request.FILES.get(name)

    def parse(self, request, name):
        f = self.get_value_from_request(request, name)

        if not isinstance(f, UploadedFile):
            f = None

        if f is None:
            self.field.parse(f, [self.IN_POS, name])

        return f
