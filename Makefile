
__VERSION__ = "0.7.16"

clean:
	rm -rf easee.egg-info dist build

lint:
	black easee --line-length 120
	flake8 --ignore=E501,E231,F403 easee

install_dev:
	pip install -r requirements-dev.txt

test:
	pytest -s -v

bump:
	bump2version --current-version $(__VERSION__) patch Makefile setup.py setup.py easee/easee.py

doc:
	rm -rf html
	pdoc --html --config show_source_code=False easee

publish_docs: doc
	git subtree push --prefix html origin gh-pages

build: clean
	python setup.py sdist bdist_wheel

publish-test:
	twine upload --repository testpypi dist/*

publish: build publish_docs
	twine upload dist/*


