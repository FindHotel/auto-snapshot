# create virtual environment
.env:
	virtualenv .env -p python2.7

# install dev requirements, and set up layer directory
develop: .env
	.env/bin/pip install -r requirements-dev.txt
	mkdir -p layers
	ln -fs ../ layers/autosnapshot

# run test suite
test:
	.env/bin/tox

# remove virtualenv and layers dir
clean:
	rm -rf .env
	rm -rf layers

# deploy the autosnapshot layer to the AWS cloud using cloudformation
create:
	humilis --profile test create --stage TEST humilis-autosnapshot.yaml

# re-deploy (using update) to the AWS cloud
update:
	humilis --profile test update --stage TEST humilis-autosnapshot.yaml

# remove everything that was deployed to AWS
delete:
	humilis --profile test delete --stage TEST humilis-autosnapshot.yaml
