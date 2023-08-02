# Replace Python version with the one installed
PYTHON=python3.9
PACKAGES=pymongo

all: layer-pymongo.zip

clean:
	- rm -rf resources
	- rm -rf .aws-sam/*
	- rm layer-pymongo.zip

layer-pymongo.zip:
	mkdir -p resources/python
	PYTHONUSERBASE=resources/python $(PYTHON) -m pip install --user $(PACKAGES)
	wget -O resources/python/global-bundle.pem https://truststore.pki.rds.amazonaws.com/global/global-bundle.pem
	cd resources && zip -r ../layer-pymongo.zip python && cd ..
	rm -rf resources

build: resources/layer-pymongo.zip template.yaml
	sam build

sam: build
	sam deploy --capabilities CAPABILITY_NAMED_IAM --guided
