
deploy:
	zip /tmp/auto-snapshot.zip *.py
	aws s3 cp /tmp/auto-snapshot.zip s3://auto-resources/lambda-functions/auto-snapshot.zip
	aws cloudformation create-stack --stack-name auto-snapshot-stack --template-body file://auto-snapshot-cloudformation-template.json --capabilities CAPABILITY_IAM

test_with_tox:
	tox

test:
    py.test
