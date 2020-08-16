from django.http import HttpResponseRedirect
from django.conf.urls import url
from django_openapi import OpenAPI, Path, Body, Query, Form, UploadFile
from django_openapi.schema import (
    BaseModel,
    StringField,
    NumberField,
    BooleanField,
    ObjectField,
    ArrayField,
)

'''
A minimal working demo of Django App
'''

DEBUG = True
SECRET_KEY = 'canukeepasecret'
ROOT_URLCONF = __name__


def redirect_to_doc(request):
    return HttpResponseRedirect('/intro/_rapidoc')


api = OpenAPI(
    title='OpenAPI Test', version='0.1', description='Just a Test', prefix_path='/intro'
)

urlpatterns = [
    url(r'^$', redirect_to_doc),
    api.as_django_url_pattern()
]


class IntroResponse1(BaseModel):
    arg1 = StringField()
    arg2 = StringField()


class IntroResponse2(BaseModel):
    arg1 = StringField(min_length=3, max_length=10)
    arg2 = NumberField(gte=0, lte=10, multiple_of=1)
    arg3 = BooleanField(default_value=False)


@api.get(
    '/get_request',
    tags=['1. Basic HTTP requests'],
    summary='Get start & create a simple http GET route',
)
def get_request():
    '''
For start using django-openapi, in your Django project

* import OpenAPI from django_openapi
* create an OpenAPI object
* put it into your urlpatterns
* start define api endpoints using api OpenAPI object


```python
from django_openapi import OpenAPI

api = OpenAPI(
    title='OpenAPI Test',
    version='0.1',
    description='Just a Test',
    prefix_path='/intro'
)

urlpatterns = [
    api.as_django_url_pattern()
]

@api.get('/get_request')
def get_request():
    return {'hello': 'world'}
```
    '''
    return {'hello': 'world'}


@api.get(
    '/get_request_with_path_args/{arg1}/{arg2}',
    tags=['1. Basic HTTP requests'],
    summary='Define path parameters',
    response_model=IntroResponse1,
)
def get_request_with_path_args(arg1=Path(), arg2=Path()):
    '''
Use `Path()` to tell API to parse parameter from url path

```python
from django_openapi import Path

@api.get('/get_request_with_path_args/{arg1}/{arg2}')
def get_request_with_path_args(arg1=Path(), arg2=Path()):
    return dict(arg1=arg1, arg2=arg2)
```
    '''
    return dict(arg1=arg1, arg2=arg2)


@api.get(
    '/get_request_with_query_args',
    tags=['1. Basic HTTP requests'],
    summary='Define query string parameters',
    response_model=IntroResponse1,
)
def get_request_with_query_args(arg1=Query(), arg2=Query()):
    '''
Use `Query()` to tell API to parse parameters from query string

```python
from django_openapi import Query

@api.get('/get_request_with_query_args')
def get_request_with_query_args(arg1=Query(), arg2=Query()):
    return dict(arg1=arg1, arg2=arg2)
```

Query strings are something after the `?` mark of your url.

`https://localhost:9527/get_request_with_query_args?arg1=1&arg2=b`

`arg1` and `arg2` are so called query string
    '''
    return dict(arg1=arg1, arg2=arg2)


@api.get(
    '/get_request_with_json_schema_query_args',
    tags=['1. Basic HTTP requests'],
    summary='Auto parameter validation via JSON schema fields',
    response_model=IntroResponse2,
)
def get_request_with_json_schema_query_args(
    arg1=Query(StringField(min_length=3, max_length=10)),
    arg2=Query(NumberField(gte=0, lte=10, multiple_of=1)),
    arg3=Query(BooleanField(default_value=False)),
):
    '''
Currently, we have 5 basic JSON schema fields

* StringField
* NumberField
* BooleanField
* ObjectField
* ArrayField

Below we'll first demo how to use StringField, NumberField & BooleanField

```python
from django_openapi import Query
from django_openapi.schema import StringField, NumberField

@api.get('/get_request_with_json_schema_query_args')
def get_request_with_json_schema_query_args(
    arg1=Query(StringField(min_length=3, max_length=10)),
    arg2=Query(NumberField(gte=0, lte=10, multiple_of=1)),
    arg3=Query(BooleanField(default_value=False)),
):
    return dict(arg1=arg1, arg2=arg2)
```
    '''
    return dict(arg1=arg1, arg2=arg2, arg3=arg3)
