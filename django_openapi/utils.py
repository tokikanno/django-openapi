# -*- coding:utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.http import JsonResponse


def json_response(data, status_code=200):
    resp = JsonResponse(data)
    resp.status_code = status_code
    return resp
