PYTHON=python3.6
PACKAGES=pymongo

all: layer-pymongo.zip

clean:
	- rm -rf resources
	- rm -rf .aws-sam/*
	- rm layer-pymongo.zip

layer-pymongo.zip:
	mkdir -p resources/python
	PYTHONUSERBASE=resources/python $(PYTHON) -m pip install --user $(PACKAGES)
	wget -O resources/python/rds-combined-ca-bundle.pem https://s3.amazonaws.com/rds-downloads/rds-combined-ca-bundle.pem
	cd resources && zip -r ../layer-pymongo.zip python && cd ..
	rm -rf resources

build: resources/layer-pymongo.zip template.yaml
	sam build

sam: build
	sam deploy --capabilities CAPABILITY_NAMED_IAM --guided
