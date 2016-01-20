# Create a symbolic link to be able to have the layer directory in the root
# directory of the repository.
develop:
	ln -fs `pwd` layers/autosnapshot


create:
	humilis --profile test create --stage TEST humilis-autosnapshot.yaml


update:
	humilis --profile test update --stage TEST humilis-autosnapshot.yaml


delete:
	humilis --profile test delete --stage TEST humilis-autosnapshot.yaml
