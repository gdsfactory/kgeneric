install:
	pip install -e .[dev,docs]
	pip install git+https://github.com/gdsfactory/kfactory.git

dev: install

test:
	pytest -s

cov:
	pytest --cov=kgeneric

mypy:
	mypy . --ignore-missing-imports

pylint:
	pylint kgeneric

ruff:
	ruff --fix kgeneric/*.py

git-rm-merged:
	git branch -D `git branch --merged | grep -v \* | xargs`

update:
	pur

update-pre:
	pre-commit autoupdate --bleeding-edge

git-rm-merged:
	git branch -D `git branch --merged | grep -v \* | xargs`

release:
	git push
	git push origin --tags

build:
	rm -rf dist
	pip install build
	python -m build

docs:
	jb build docs

.PHONY: drc doc docs
