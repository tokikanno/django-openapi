# Basic Django settings
DEBUG = True
SECRET_KEY = 'secret'
ROOT_URLCONF = __name__


# import OpenAPI from django_opeanapi
from django_openapi import OpenAPI

# create an API object instance
api = OpenAPI(title='My OpenAPI Test', prefix_path='/test_api')

# Add API object into urlpatterns
urlpatterns = [api.as_django_url_pattern()]


# Now let's try adding some basic routes for you API
from django_openapi import Path, Body, Query, Form


@api.get('/test/hello_via_path/{word}', tags=['test'])
def hello_via_path(word=Path()):
    return {'hello': word}


@api.get('/test/hello_via_query', tags=['test'])
def hello_via_query(word=Query()):
    return {'hello': word}


@api.post('/test/hello_via_form', tags=['test'])
def hello_via_form(word=Form()):
    return {'hello': word}


# Advanced routes via JSON body & JSON schema object
from django_openapi import Body
from django_openapi.schema import BaseModel, StringField


class HelloPayload(BaseModel):
    word = StringField(default_value='world', min_length=3)


@api.post('/test/hello_via_json_body', tags=['test'])
def hello_via_json_body(payload=Body(HelloPayload)):
    return {'hello': payload.word}
