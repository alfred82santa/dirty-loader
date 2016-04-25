

help:
	@echo "Options"
	@echo "---------------------------------------------------------------"
	@echo "help:                     This help"
	@echo "requirements:             Download requirements"
	@echo "requirements-test:        Download requirements for tests"
	@echo "requirements-docs:        Download requirements for docs"
	@echo "run-tests:                Run tests with coverage"
	@echo "publish:                  Publish new version on Pypi"
	@echo "clean:                    Clean compiled files"
	@echo "flake:                    Run Flake8"
	@echo "prepush:                  Helper to run before to push to repo"
	@echo "autopep:                  Reformat code using PEP8"
	@echo "---------------------------------------------------------------"

requirements:
	@echo "Installing dirty-loader requirements..."
	pip install -r requirements.txt

requirements-test:
	@echo "Installing dirty-loader tests requirements..."
	@make requirements
	pip install -r requirements-test.txt

requirements-docs:
	@echo "Installing dirty-loader docs requirements..."
	@make requirements
	pip install -r requirements-docs.txt

run-tests:
	@echo "Running tests..."
	nosetests --with-coverage -d --cover-package=dirty_loader -x

publish:
	@echo "Publishing new version on Pypi..."
	python setup.py sdist upload

clean:
	@echo "Cleaning compiled files..."
	find . | grep -E "(__pycache__|\.pyc|\.pyo)$ " | xargs rm -rf

flake:
	@echo "Running flake8 tests..."
	flake8 dirty_loader
	flake8 tests

autopep:
	autopep8 --max-line-length 120 -r -j 8 -i .

prepush:
	@make flake
	@make run-tests

