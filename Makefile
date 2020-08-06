.PHONY: build demo


build:
	python setup.py sdist bdist_wheel

demo:
	django-admin runserver --pythonpath=. --settings=demo.app 9527
