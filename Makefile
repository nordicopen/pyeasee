
__VERSION__ = "0.7.0"

bump:
	bump2version --current-version $(__VERSION__) patch Makefile setup.py setup.py easee/easee.py

build:
	python setup.py sdist bdist_wheel
