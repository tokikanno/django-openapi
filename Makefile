.PHONY: clean build demo upload-test

clean:
	rm -rf build dist

build:
	python setup.py sdist bdist_wheel

demo:
	django-admin runserver --pythonpath=. --settings=demo.app 9527

upload-prod:
	twine upload -u __token__ dist/*

upload-test:
	twine upload -u __token__ --repository testpypi dist/*
