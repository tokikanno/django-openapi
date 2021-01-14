from os import path
from hashlib import md5
from datetime import datetime

from django.http import HttpResponseRedirect
from django.conf.urls import url
from django_openapi import OpenAPI, Path, Body, Query, Form, UploadFile, Cookie, Header
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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': path.join(path.dirname(__file__), 'db.sqlite3'),
    }
}


def redirect_to_doc(request):
    return HttpResponseRedirect(
        '/intro/_rapidoc#tag--1.-Setup-your-first-OpenAPI-endpoint'
    )


api = OpenAPI(
    title='OpenAPI Test', version='0.1', description='Just a Test', prefix_path='/intro'
)

urlpatterns = [url(r'^$', redirect_to_doc), api.as_django_url_pattern()]


class IntroResponse1(BaseModel):
    arg1 = StringField()
    arg2 = StringField()


class IntroResponse2(BaseModel):
    arg1 = StringField(min_length=3, max_length=10)
    arg2 = NumberField(gte=0, lte=10, multiple_of=1)
    arg3 = BooleanField(default_value=False)


@api.get(
    '/get_request',
    tags=['1. Setup your first OpenAPI endpoint'],
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
from django_openapi.schema import StringField, NumberField, BooleanField

@api.get('/get_request_with_json_schema_query_args')
def get_request_with_json_schema_query_args(
    arg1=Query(StringField(min_length=3, max_length=10)),
    arg2=Query(NumberField(gte=0, lte=10, multiple_of=1)),
    arg3=Query(BooleanField(default_value=False)),
):
    return dict(arg1=arg1, arg2=arg2, arg3=arg3)
```
    '''
    return dict(arg1=arg1, arg2=arg2, arg3=arg3)


@api.post(
    '/post_request_with_json_schema_form_args',
    tags=['1. Basic HTTP requests'],
    summary='Define Form parameters',
    response_model=IntroResponse2,
)
def post_request_with_json_schema_form_args(
    arg1=Form(StringField(min_length=3, max_length=10)),
    arg2=Form(NumberField(gte=0, lte=10, multiple_of=1)),
    arg3=Form(BooleanField(default_value=False)),
):
    '''
Now we use the same JSON schema field definitions, but in Form() format.

```python
from django_openapi import Form
from django_openapi.schema import StringField, NumberField, BooleanField

@api.post('/post_request_with_json_schema_form_args')
def post_request_with_json_schema_form_args(
    arg1=Form(StringField(min_length=3, max_length=10)),
    arg2=Form(NumberField(gte=0, lte=10, multiple_of=1)),
    arg3=Form(BooleanField(default_value=False)),
):
    return dict(arg1=arg1, arg2=arg2, arg3=arg3)
```
    '''
    return dict(arg1=arg1, arg2=arg2, arg3=arg3)


@api.post(
    '/post_request_file_upload',
    tags=['1. Basic HTTP requests'],
    summary='Define File Upload',
)
def post_request_file_upload(
    upload_file=UploadFile(),
    md5_hash=Form(StringField(required=False, description='md5 of uploaded file')),
):
    '''
Now let's try building an endpoint for user file upload.

```python
from hashlib import md5
from django_openapi import UploadFile, Form
from django_openapi.schema import StringField, NumberField, BooleanField

@api.post('/post_request_file_upload')
def post_request_file_upload(
    upload_file = UploadFile(),
    md5_hash = Form(StringField(required=False, description='md5 of uploaded file'))
):
    return {
        'submitted_md5': md5_hash,
        'file': {
            'name': upload_file.name,
            'size': upload_file.size,
            'md5': md5(upload_file.read()).hexdigest,
        },
    }
```
    '''
    return {
        'submitted_md5': md5_hash,
        'file': {
            'name': upload_file.name,
            'size': upload_file.size,
            'md5': md5(upload_file.read()).hexdigest(),
        },
    }


class SamplePayload(BaseModel):
    arg1 = StringField(min_length=3, max_length=10)
    arg2 = NumberField(gte=0, lte=10, multiple_of=1)
    arg3 = BooleanField(default_value=False)


class SampleResponse(BaseModel):
    obj = ObjectField(SamplePayload)
    ary = ArrayField(ObjectField(SamplePayload))


@api.post(
    '/post_request_with_json_schema_body',
    tags=['1. Basic HTTP requests'],
    summary='Define body parameters via JSON schema model',
    response_model=SampleResponse,
)
def post_request_with_json_schema_body(payload=Body(SamplePayload)):
    '''
The JSON schema fields could also be used for describing JSON body format, 
all you need is declearing a class inherited from BaseModel class.

```python
from django_openapi import Body
from django_openapi.schema import BaseModel, StringField, NumberField, BooleanField

class SamplePayload(BaseModel):
    arg1 = StringField(min_length=3, max_length=10)
    arg2 = NumberField(gte=0, lte=10, multiple_of=1)
    arg3 = BooleanField(default_value=False)

class SampleResponse(BaseModel):
    obj = ObjectField(SamplePayload)  # Object (dict in JSON) type field
    ary = ArrayField(ObjectField(SamplePayload))  # Array type field


@api.post(
    '/post_request_with_json_schema_body', 
    response_model=SampleResponse,  # you can also put json schema model here for declearing response model 
)
def post_request_with_json_schema_body(
    payload=Body(SamplePayload),
):
    return payload
```
    '''
    return {'obj': payload, 'ary': [payload, payload]}


@api.post(
    '/some_special_variables_by_name',
    tags=['1. Basic HTTP requests'],
    summary='Some special variables',
)
def some_special_variables_by_name(request, session, cookie_jar):
    '''
You could access some special variables via your function parameter name.

* `request`

  * the django `HttpRequest` object

* `session`

  * the session object binded on request

* `cookie_jar`

  * if you want to set/del cookies on the response object, you must use cookie_jar
  * cookie_jar is a proxy object to real HttpResponse object. The `set_cookie()`, `delete_cookie()` functions on it have the same signatures of HttpResonse.

```python
@api.get(
    '/some_special_variables_by_name',
)
def some_special_variables_by_name(request, session, cookie_jar):

    # this has the same signature as django HTTPResponse.set_cookie() function
    cookie_jar.set_cookie('test_cookie', str(datetime.now()))

    return {
        'request': request,
        'session': session,
    }
```
    '''

    # this has the same signature as django HTTPResponse.set_cookie() function
    cookie_jar.set_cookie('test_cookie', str(datetime.now()))

    return {
        'request': repr(request),
        'session': session,
    }


@api.post(
    '/other_argument_data_sources',
    tags=['1. Basic HTTP requests'],
    summary='Other argument data sources',
)
def other_argument_data_sources(
    test_cookie=Cookie(), content_type=Header(), http_referer=Header()
):
    '''
You can also get your request arguments from other data sources.

Like: `Header()`, `Cookie()`

* *Note: While accessing via `Header()`, all variable name will converted to uppercase as http header key name*
* *e.g.: `content_type` -> `CONTENT_TYPE`

```python
@api.post(
    '/other_argument_data_sources',
)
def other_argument_data_sources(
    test_cookie=Cookie(), content_type=Header(), http_referer=Header()
):
    return {
        'test_cookie': test_cookie,
        'content_type': content_type,
        'referrer': http_referer,
    }
```
    '''
    return {
        'test_cookie': test_cookie,
        'content_type': content_type,
        'referrer': http_referer,
    }

