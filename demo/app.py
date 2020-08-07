# -*- coding:utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from collections import OrderedDict

import six

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


USER_STORE = OrderedDict()

UID_FIELD = NumberField(gt=0, multiple_of=1)


class CreateUserModel(BaseModel):
    first_name = StringField(min_length=5, max_length=50)
    last_name = StringField(min_length=5, max_length=50)


class UserModel(CreateUserModel):
    uid = UID_FIELD


@api.get('/users', tags=['users'])
def get_users():
    return {'user': list(six.itervalues(USER_STORE))}


@api.get('/users/{uid}', tags=['users'])
def get_user_by_uid(uid=Path(UID_FIELD)):
    return {'user': USER_STORE.get(uid)}


@api.post('/users', tags=['users'])
def create_user(payload=Body(CreateUserModel)):
    uid = 1 if not USER_STORE else (max(six.iterkeys(USER_STORE)) + 1)
    user = UserModel(
        uid=uid, first_name=payload.first_name, last_name=payload.last_name
    )
    USER_STORE[uid] = user

    return user


urlpatterns = [url(r'^$', home), api.as_django_url_pattern()]
