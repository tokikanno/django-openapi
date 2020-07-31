# -*- coding:utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from django_openapi.schema.fields.string import StringField

from django.conf.urls import url
from django.http import HttpResponse

from django_openapi import OpenAPI, Path, Body, Query, Form, UploadFile
from django_openapi.schema import (
    BaseModel,
    StringField,
    NumberField,
    ObjectField,
    ArrayField,
)

'''
A minimal working demo of Django App
'''

DEBUG = True
SECRET_KEY = 'thisisagoooooooooooooooooooooooooooooodaytotie'
ROOT_URLCONF = __name__


def home(request):
    return HttpResponse('Welcome Home')


api = OpenAPI(
    title='OpenAPI Test', version='0.1', description='Just a Test', prefix_path='/api'
)


@api.get('/users')
def get_users():
    return {'user': []}


@api.get('/users/{uid}')
def get_user_by_uid(uid=Path(NumberField(gt=0, multiple_of=1))):
    return {'uid': uid}


urlpatterns = [url(r'^$', home), api.as_django_url_pattern()]
