.env:
	virtualenv .env -p python2.7

develop: .env
	.env/bin/pip install -r requirements-dev.txt

clean:
	rm -rf .env

test:
	.env/bin/python -m pytest tests
