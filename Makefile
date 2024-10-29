clean:
	rm -rf pyeasee.egg-info dist build

lint:
	isort src
	black src --line-length 120
	flake8 --ignore=E501,E231,F403 src

install_dev:
	pip install -r requirements-dev.txt

test:
	pytest -s -v

bump:
	bump2version --allow-dirty patch setup.py src/pyeasee/easee.py

doc:
	rm -rf html
	pdoc --html --config show_source_code=False src/pyeasee

publish_docs: doc
	git subtree push --prefix html origin gh-pages
	# git push origin `git subtree split --prefix html master`:gh-pages --force

build: clean
	python setup.py sdist bdist_wheel

publish-test:
	twine upload --repository testpypi dist/*

publish: build publish_docs
	twine upload dist/*
