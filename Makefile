
docker_image_tag=iam_bakery
aws_default_region=ap-southeast-2

define HELP_TEXT
Usage: make [TARGET]...
Available targets:
endef
export HELP_TEXT
help: ## help target
		@echo "$$HELP_TEXT"
		@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / \
			{printf "\033[36m%-30s\033[0m  %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build-docker-image:
	@docker build -f docker/Dockerfile -t $(docker_image_tag) .

deploy-bakery-cf: ## run ansible deploy playbook
	ansible-playbook deploy_cloudformation/deploy_bakery.yml -vvv \
		-e PROFILE=default \
		-e REGION=$(aws_default_region)\
		-e AWS_ACCESS_KEY_ID \
		-e AWS_SECRET_ACCESS_KEY \
		-e AWS_SESSION_TOKEN \
		-e AWS_DEFAULT_REGION=$(aws_default_region) \
		-e prefix=$(prefix)\
		-e bakery_cf_bucket=$(bakery_cf_bucket)

# example: make deploy-bakery-cf-in-docker prefix=test- bakery_cf_bucket=test-bakery-cf
deploy-bakery-cf-in-docker: build-docker-image ## deploy cloudformation templates in docker
	@docker run -i \
		-v $(PWD):/data \
		-e PROFILE=default \
		-e REGION=$(aws_default_region) \
		-e AWS_DEFAULT_REGION=$(aws_default_region) \
		-e AWS_ACCESS_KEY_ID \
		-e AWS_SECRET_ACCESS_KEY \
		-e AWS_SESSION_TOKEN \
		-e prefix=$(prefix) \
		-e bakery_cf_bucket=$(bakery_cf_bucket) \
		$(docker_image_tag) \
		/bin/sh -c "make deploy-bakery-cf"

bootstrap-assume-script: ## Creates assume.sh Usage: source assume.sh
	$$(which python) utils/bootstrap_assume_script.py
	chmod +x assume.sh
	ln -s $$(pwd)/assume.sh /usr/local/bin/assume
