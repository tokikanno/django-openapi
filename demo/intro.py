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
SECRET_KEY = 'canukeepasecret'
ROOT_URLCONF = __name__


api = OpenAPI(
    title='OpenAPI Test', version='0.1', description='Just a Test', prefix_path='/intro'
)

urlpatterns = [api.as_django_url_pattern()]


@api.get(
    '/simple_get_request',
    tags=['1. Basic HTTP requests'],
    summary='A simple http GET request',
)
def simple_get_request():
    '''
```python
@api.get('/simple_get_request')
def simple_get_request():
    return {}
```
    '''
    return {'hello': 'world'}


@api.get(
    '/simple_get_request_with_path_args/{arg1}/{arg2}',
    tags=['1. Basic HTTP requests'],
    summary='A simple http GET request which parse path as arguments',
)
def simple_get_request_with_path_args(arg1=Path(), arg2=Path()):
    '''
```python
from django_openapi import Path

@api.get('/simple_get_request_with_path_args/{arg1}/{arg2}')
def simple_get_request_with_path_args(arg1=Path(), arg2=Path()):
    return dict(arg1=arg1, arg2=arg2)
```
    '''
    return dict(arg1=arg1, arg2=arg2)


@api.get(
    '/simple_get_request_with_path_args',
    tags=['1. Basic HTTP requests'],
    summary='A simple http GET request which parse query string as arguments',
)
def simple_get_request_with_query_args(arg1=Query(), arg2=Query()):
    '''
```python
from django_openapi import Query

@api.get('/simple_get_request_with_query_args')
def simple_get_request_with_query_args(arg1=Query(), arg2=Query()):
    return dict(arg1=arg1, arg2=arg2)
```
    '''
    return dict(arg1=arg1, arg2=arg2)


@api.get(
    '/simple_get_request_with_formatted_query_args',
    tags=['1. Basic HTTP requests'],
    summary='A simple http GET request which parse query string by special format rules',
)
def simple_get_request_with_formatted_query_args(
    arg1=Query(StringField(min_length=3, max_length=10)),
    arg2=Query(NumberField(gte=0, lte=10)),
):
    '''
```python
from django_openapi import Query
from django_openapi.schema import StringField, NumberField

@api.get('/simple_get_request_with_formatted_query_args')
def simple_get_request_with_formatted_query_args(
    arg1=Query(StringField(min_length=3, max_length=10)),
    arg2=Query(NumberField(gte=0, lte=10))
):
    return dict(arg1=arg1, arg2=arg2)
```
    '''
    return dict(arg1=arg1, arg2=arg2)
