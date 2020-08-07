.PHONY: build demo upload-test


build:
	python setup.py sdist bdist_wheel

demo:
	django-admin runserver --pythonpath=. --settings=demo.app 9527

upload:
	twine upload -u __token__ dist/*

upload-test:
	twine upload -u __token__ --repository testpypi dist/*
