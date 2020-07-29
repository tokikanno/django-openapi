# -*- coding:utf8 -*-
from __future__ import unicode_literals
from __future__ import print_function

from collections import OrderedDict
from pinkoi.base.openapi.schema.base import BaseModel

import six

from .route import Route

from django.http import HttpResponse, Http404, HttpResponseNotAllowed
from pinkoi.lib.json import json_response

DOC_PAGE_TPL = '''<!DOCTYPE html>
<html>
<head>
    <link type="text/css" rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui.css">
    <link rel="shortcut icon" href="https://fastapi.tiangolo.com/img/favicon.png">
    <title>Pinkoi Business Site - Swagger UI</title>
</head>
<body>
    <div id="swagger-ui">
    </div>
    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui-bundle.js"></script>
    <!-- `SwaggerUIBundle` is now available on the page -->
    <script>
    const ui = SwaggerUIBundle({{
        url: '{prefix_path}/_openapi.json',
        oauth2RedirectUrl: window.location.origin + '/docs/oauth2-redirect',
        dom_id: '#swagger-ui',
        presets: [
            SwaggerUIBundle.presets.apis,
            SwaggerUIBundle.SwaggerUIStandalonePreset
        ],
        layout: "BaseLayout",
        deepLinking: true
    }})
    </script>
</body>
</html>'''

REDOC_PAGE_TPL = '''
<!DOCTYPE html>
<html>
    <head>
        <title>Pinkoi Business Site - ReDoc</title>
        <!-- needed for adaptive design -->
        <meta charset="utf-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1">

        <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">

        <link rel="shortcut icon" href="https://fastapi.tiangolo.com/img/favicon.png">
        <!--
        ReDoc doesn't change outer page styles
        -->
        <style>
        body {{
            margin: 0;
            padding: 0;
        }}
        </style>
    </head>
    <body>
    <redoc spec-url="{prefix_path}/_openapi.json"></redoc>
    <script src="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js"> </script>
    </body>
</html>'''


class OpenAPI(object):
    def __init__(
        self,
        title='OpenAPI',  # REQUIRED. The title of the API.
        version='0.0',  # REQUIRED. The version of the OpenAPI document
        description='',  # A short description of the API. CommonMark syntax
        prefix_path='',
        server_url='',
        server_description='',
    ):
        self.title = title
        self.description = description
        self.version = version
        self.path_route_map = OrderedDict()
        self.prefix_path = prefix_path
        self.server_info_d = {
            'url': server_url,
            'description': server_description,
        }

    def add_route(
        self,
        route_path,
        allow_methods=tuple(),
        summary='',
        description='',
        tags=tuple(),
        response_model=None,
        response_model_map=None,
    ):
        def _decorator(fn):
            route = Route(
                fn,
                route_path=route_path,
                allow_methods=allow_methods,
                summary=summary,
                description=description,
                tags=tags,
                response_model=response_model,
                response_model_map=response_model_map,
            )

            assert (
                route_path not in self.path_route_map
            ), '{} already in path_route_map'.format(route_path)

            self.path_route_map[route_path] = route

            return fn

        return _decorator

    def get(
        self,
        route_path,
        summary='',
        description='',
        tags=tuple(),
        response_model=None,
        response_model_map=None,
    ):
        return self.add_route(
            route_path=route_path,
            allow_methods=['GET'],
            summary=summary,
            description=description,
            tags=tags,
            response_model=response_model,
            response_model_map=response_model_map,
        )

    def post(
        self,
        route_path,
        summary='',
        description='',
        tags=tuple(),
        response_model=None,
        response_model_map=None,
    ):
        return self.add_route(
            route_path=route_path,
            allow_methods=['POST'],
            summary=summary,
            description=description,
            tags=tags,
            response_model=response_model,
            response_model_map=response_model_map,
        )

    def get_openapi_schema(self):
        api_d = {
            'openapi': '3.0.2',
            'info': {
                'title': self.title,
                'description': self.description,
                'version': self.version,
            },
            'servers': [self.server_info_d],
        }

        api_d['paths'] = path_d = OrderedDict()

        for route_path, route_obj in six.iteritems(self.path_route_map):
            api_d['paths'][route_path] = route_obj.get_openapi_schema()

        api_d['components'] = {
            'schemas': BaseModel.get_ref_name_to_schema_map()
        }

        return api_d

    def as_django_view(self):
        def dispatcher(request, route_path):
            route_path = (
                route_path[:-1] if route_path.endswith('/') else route_path
            )

            # document routes
            if route_path == '/_openapi.json':
                return json_response(self.get_openapi_schema())
            elif route_path == '/_docs':
                return HttpResponse(
                    DOC_PAGE_TPL.format(prefix_path=self.prefix_path)
                )
            elif route_path == '/_redoc':
                return HttpResponse(
                    REDOC_PAGE_TPL.format(prefix_path=self.prefix_path)
                )

            # find route handler from path_route_map
            route = self.path_route_map.get(route_path)
            if route:
                if request.method not in route.allow_methods:
                    return json_response({}, status_code=405)

                # route.__call__
                return route(request)

            return json_response({}, status_code=404)

        return dispatcher
