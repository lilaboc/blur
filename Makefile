install: requirements.txt
	python3 -m pip install --upgrade pip
	python3 -m pip install -e .
wheel: requirements.txt
	python3 -m build --wheel
	python3 setup.py clean --all
requirements.txt: Pipfile.lock
	pipenv requirements > requirements.txt