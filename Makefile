install: install-dev
	@ pip install --upgrade pip
	@ pip install -r requirements.txt
	@ pip install .

install-dev:
	@ pip install --upgrade pip
	@ pip install -r requirements.dev.txt

test: test-unit

test-unit:
	@ tox -e unit
