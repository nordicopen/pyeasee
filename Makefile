
__VERSION__ = "0.7.30"

clean:
	rm -rf pyeasee.egg-info dist build

lint:
	black pyeasee --line-length 120
	flake8 --ignore=E501,E231,F403 pyeasee

install_dev:
	pip install -r requirements-dev.txt

test:
	pytest -s -v

bump:
	bump2version --current-version $(__VERSION__) patch Makefile setup.py setup.py pyeasee/easee.py

doc:
	rm -rf html
	pdoc --html --config show_source_code=False pyeasee

publish_docs: doc
	git subtree push --prefix html origin gh-pages
	# git push origin `git subtree split --prefix html master`:gh-pages --force

build: clean
	python setup.py sdist bdist_wheel

publish-test:
	twine upload --repository testpypi dist/*

publish: build publish_docs
	twine upload dist/*


