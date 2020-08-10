.PHONY: clean build demo upload-test

clean:
	rm -rf build dist

build:
	python setup.py sdist bdist_wheel

demo-django:
	django-admin runserver --pythonpath=. --settings=demo.django_app 9527

upload:
	twine upload -u __token__ dist/*

upload-test:
	twine upload -u __token__ --repository testpypi dist/*
