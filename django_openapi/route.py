# -*- coding:utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from inspect import getargspec
from string import Formatter
from collections import OrderedDict
import re

from django.http import HttpResponse

from .utils import json_response
from .params import BaseRequestParam
from .cookie import CookieJar
from .schema import (
    BaseModel,
    StringField,
    ArrayField,
    ObjectField,
    SchemaValidationError,
)

from collections import Counter, defaultdict, OrderedDict

import six


ALLOW_HTTP_METHOD_SET = {
    'GET',
    'POST',
    'PUT',
    'DELETE',
    'PATCH',
    'HEAD',
    'TRACE',
}


class RouteConfig(BaseModel):
    route_path = StringField(required=True, min_length=1, regex=r'^/')
    allow_methods = ArrayField(StringField(enums=ALLOW_HTTP_METHOD_SET), min_items=1)
    summary = StringField(default_value=None, required=False)
    description = StringField(default_value=None, required=False)
    tags = ArrayField(StringField())


class ValidationErrorItem(BaseModel):
    loc = ArrayField(StringField())
    msg = StringField()
    type = StringField()


class ValidationErrorResponse(BaseModel):
    deatil = ArrayField(ObjectField(ValidationErrorItem))


class PathNotFullfilled(Exception):
    pass


PATH_NOT_FULL_FILLED = object()


class RoutePath(object):
    def __init__(self, route_path):
        route_path = six.ensure_text(route_path)
        assert route_path.startswith('/')

        self.org_route_path = route_path
        # route_path = route_path[1:]
        self.route_path = route_path[:-1] if route_path.endswith('/') else route_path

        self.key_set = set()
        re_segs = []
        fmt = Formatter()
        for prefix, key, fmt_spec, conversion in fmt.parse(self.route_path):
            if key is None:
                re_segs.append(prefix)
                continue

            assert key and not fmt_spec and not conversion, (
                'fail parsing parameter from path: ' + self.route_path
            )
            assert key not in self.key_set, 'duplicated key {}'.format(key)
            self.key_set.add(key)
            re_segs.append('{prefix}(?P<{key}>[^/]+)'.format(prefix=prefix, key=key))

        # print('regex: ' + ''.join(re_segs))
        self.regex = re.compile('^' + ''.join(re_segs) + '$')

    def parse(self, request_path):
        if not request_path.startswith('/'):
            request_path = '/' + request_path

        match = self.regex.match(request_path)
        if not match:
            return PATH_NOT_FULL_FILLED

        return match.groupdict()


class Route(object):
    def __init__(
        self,
        fn,
        route_path,
        allow_methods=None,
        summary=None,
        description=None,
        tags=tuple(),
        response_model=None,
        response_model_map=None,
    ):
        description = description or fn.__doc__

        cfg = RouteConfig(
            route_path=route_path,
            allow_methods=allow_methods,
            summary=summary,
            description=description,
            tags=tags,
        )

        if route_path.endswith('/'):
            route_path = route_path[:-1]

        self.route_path = route_path
        self.path_parser = RoutePath(route_path)
        self.allow_methods = cfg.allow_methods
        self.summary = cfg.summary
        self.description = cfg.description
        self.tags = cfg.tags

        self.response_map = {200: BaseModel, 422: ValidationErrorResponse}
        if response_model:
            assert isinstance(response_model, type) and issubclass(
                response_model, BaseModel
            )
            self.response_map[200] = response_model

        if response_model_map and isinstance(response_model_map, dict):
            for k, v in response_model_map.items():
                assert (
                    isinstance(k, int) and 100 <= k < 1000
                ), 'Bad HTTP status code {}'.format(k)
                assert isinstance(v, type) and issubclass(
                    v, BaseModel
                ), 'Must be OpenAPI BaseModel'
                response_model_map[k] = v

        self.arg_type_counter = Counter()
        self.arg_name_to_request_param_map = OrderedDict()
        self.pass_request = False
        self.pass_session = False
        self.pass_cookie_jar = False
        self._body_form_cls = None

        arg_spec = getargspec(fn)
        if arg_spec.args and arg_spec.defaults:
            arg_default_len_diff = len(arg_spec.args) - len(arg_spec.defaults)
            for i in range(len(arg_spec.args)):
                name = arg_spec.args[i]
                vidx = i - arg_default_len_diff
                value = arg_spec.defaults[vidx] if vidx >= 0 else None
                # print(name, value)

                if name == 'request':
                    self.pass_request = True

                elif name == 'session':
                    self.pass_session = True

                elif name == 'cookie_jar':
                    self.pass_cookie_jar = True

                elif isinstance(value, BaseRequestParam):
                    assert (
                        name not in self.arg_name_to_request_param_map
                    ), 'duplicated arg name'
                    self.arg_name_to_request_param_map[name] = value
                    self.arg_type_counter[value.IN_POS] += 1

                else:
                    raise ValueError('unmapped parameter {}'.format(name))

        if self.path_parser.key_set:
            for k in self.path_parser.key_set:
                assert (
                    k in self.arg_name_to_request_param_map
                    and self.arg_name_to_request_param_map[k].IN_POS == 'path'
                ), 'umapped path arg key {}'.format(k)

        assert (
            self.arg_type_counter['body'] <= 1
        ), 'can only has single Body param in same route'

        assert (
            self.arg_type_counter['body'] == 0 or self.arg_type_counter['form'] == 0
        ), 'can not define both form/body param in same route'

        self.fn = fn

    def get_openapi_schema(self):
        route_d = {}

        if self.summary:
            route_d['summary'] = self.summary
        if self.description:
            route_d['description'] = self.description
        if self.tags:
            route_d['tags'] = self.tags

        form_param_d = OrderedDict()
        parameters = []
        for name, param in six.iteritems(self.arg_name_to_request_param_map):
            if param.IN_POS == 'body':
                route_d['requestBody'] = param.get_openapi_schema()

            elif param.IN_POS == 'form':
                form_param_d[name] = param.field

            else:
                parameters.append(param.get_openapi_schema(name))

        if parameters:
            route_d['parameters'] = parameters

        if form_param_d and 'requestBody' not in route_d:
            if self._body_form_cls is None:
                self._body_form_cls = type(
                    six.ensure_str(
                        '{route_path}_body_form'.format(
                            route_path=self.route_path.replace('/', '_')
                        )
                    ),
                    (BaseModel,),
                    form_param_d,
                )

            route_d['requestBody'] = {
                'content': {
                    'multipart/form-data': {
                        # 'application/x-www-form-urlencoded': {
                        'schema': {
                            '$ref': '#/components/schemas/'
                            + self._body_form_cls.get_json_schema_ref()
                        }
                    }
                }
            }

        if self.response_map:
            route_d['responses'] = {
                six.text_type(k): {
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/'
                                + v.get_json_schema_ref()
                            }
                        }
                    }
                }
                for k, v in self.response_map.items()
            }

        json_d = {m.lower(): route_d for m in self.allow_methods}
        return json_d

    def match_path(self, request_path):
        return self.path_parser.parse(request_path)

    def prase_response(self, resp, http_status_code=200):

        resp = resp or {}  # default empty dict response
        resp_model_cls = self.response_map.get(http_status_code)

        if isinstance(resp, HttpResponse):
            return resp

        if isinstance(resp, dict):
            if resp_model_cls:
                resp = resp_model_cls(**resp)
            else:
                return json_response(resp)

        if isinstance(resp, BaseModel) and (
            not resp_model_cls or isinstance(resp, resp_model_cls)
        ):
            return json_response(resp.to_json_dict())

        raise ValueError(
            'unable to process resp of {route_path}'.format(route_path=self.route_path)
        )

    def __call__(self, request):
        kwargs = {}

        if self.pass_request:
            kwargs['request'] = request

        if self.pass_session:
            kwargs['session'] = request.session

        if self.pass_cookie_jar:
            kwargs['cookie_jar'] = CookieJar()

        validation_errors = []
        for k, field in six.iteritems(self.arg_name_to_request_param_map):
            try:
                kwargs[k] = field.parse(request, k)
            except SchemaValidationError as e:
                validation_errors.append(e)

        if validation_errors:
            return json_response(
                {
                    'detail': [
                        {
                            'loc': err.position,
                            'type': err.err_type,
                            'msg': err.err_type,
                        }
                        for err in validation_errors
                    ]
                },
                status_code=422,
            )

        resp = self.fn(**kwargs)
        resp = self.prase_response(resp)

        if self.pass_cookie_jar:
            kwargs['cookie_jar'].apply_to_response(resp)

        return resp

    def __repr__(self):
        return 'Route("{}")'.format(self.route_path)
