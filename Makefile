# make humilis look for the autosnapshot layer in this directory
develop:
	ln -fs `pwd` layers/autosnapshot

# deploy the autosnapshot layer to the AWS cloud using cloudformation
create:
	humilis --profile test create --stage TEST humilis-autosnapshot.yaml

# re-deploy (using update) to the AWS cloud
update:
	humilis --profile test update --stage TEST humilis-autosnapshot.yaml

# remove everything that was deployed to AWS
delete:
	humilis --profile test delete --stage TEST humilis-autosnapshot.yaml
