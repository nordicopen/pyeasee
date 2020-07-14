
__VERSION__ = "0.7.4"

bump:
	bump2version --current-version $(__VERSION__) patch Makefile setup.py setup.py easee/easee.py

clean:
	rm -rf easee.egg-info dist build

build: clean
	python setup.py sdist bdist_wheel

publish-test:
	twine upload --repository testpypi dist/*

publish: build
	twine upload dist/*
