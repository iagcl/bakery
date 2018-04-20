# Copyright 2017 Insurance Australia Group Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
export LOCATION_CORE=.
export PYTHONPATH=$(LOCATION_CORE)

AWS_DEFAULT_REGION=ap-southeast-2
DOCKER_IMAGE=iam_bakery

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
	@docker build -f docker/Dockerfile -t $(DOCKER_IMAGE) .

create-bakery-cf:
	cp $(LOCATION_CORE)/deploy_cloudformation/bakery/templates/bakery_stack.tmpl $(LOCATION_CORE)/deploy_cloudformation/bakery/bakery_stack.yml
	cp $(LOCATION_CORE)/deploy_cloudformation/bakery/templates/bakery_account.tmpl $(LOCATION_CORE)/deploy_cloudformation/bakery/bakery_account.yml
	python $(LOCATION_CORE)/python_lib/create_bakery_env_cf.py

deploy-bakery-cf: create-bakery-cf ## deploy bakery
	ansible-playbook $(LOCATION_CORE)/deploy_cloudformation/deploy_bakery.yml -vvv \
		-e REGION=$(AWS_DEFAULT_REGION) \
		-e AWS_ACCESS_KEY_ID \
		-e AWS_SECRET_ACCESS_KEY \
		-e AWS_SESSION_TOKEN \
		-e prefix=$(prefix) \
		-e bakery_cf_bucket=$(bakery_cf_bucket)

# example: make deploy-bakery-cf-in-docker prefix=test- bakery_cf_bucket=test-bakery-cf
deploy-bakery-cf-in-docker: build-docker-image ## deploy bakery in docker
	@docker run -i \
		-v $(PWD):/data \
		-e AWS_ACCESS_KEY_ID \
		-e AWS_SECRET_ACCESS_KEY \
		-e AWS_SESSION_TOKEN \
		-e AWS_DEFAULT_REGION=$(AWS_DEFAULT_REGION) \
		-e prefix=$(prefix) \
		-e bakery_cf_bucket=$(bakery_cf_bucket) \
		$(DOCKER_IMAGE) \
		/bin/bash -c "make deploy-bakery-cf"

deploy-check-admin-access-cf: ## deploy check admin access
	ansible-playbook $(LOCATION_CORE)/deploy_cloudformation/deploy_check_admin_access.yml -vvv \
		-e REGION=$(AWS_DEFAULT_REGION) \
		-e AWS_ACCESS_KEY_ID \
		-e AWS_SECRET_ACCESS_KEY \
		-e AWS_SESSION_TOKEN \
		-e prefix=$(prefix) \
		-e bakery_cf_bucket=$(bakery_cf_bucket)

# example: make deploy-check-admin-access-cf-in-docker prefix=test- bakery_cf_bucket=test-bakery-cf
deploy-check-admin-access-cf-in-docker: build-docker-image ## deploy check admin access in docker
	@docker run -i \
		-v $(PWD):/data \
		-e AWS_ACCESS_KEY_ID \
		-e AWS_SECRET_ACCESS_KEY \
		-e AWS_SESSION_TOKEN \
		-e AWS_DEFAULT_REGION=$(AWS_DEFAULT_REGION) \
		-e prefix=$(prefix) \
		-e bakery_cf_bucket=$(bakery_cf_bucket) \
		$(DOCKER_IMAGE) \
		/bin/bash -c "make deploy-check-admin-access-cf"

bootstrap-assume-script: ## creates assume.sh Usage: source assume.sh
	$$(which python) $(LOCATION_CORE)/utils/bootstrap_assume_script.py
	chmod +x assume.sh

create-burger-cf:
	python $(LOCATION_CORE)/python_lib/create_burger_account_cf.py

deploy-burger-cf: create-burger-cf ## deploy burger
	ansible-playbook $(LOCATION_CORE)/deploy_cloudformation/deploy_burger.yml -vvv \
		-e REGION=$(AWS_DEFAULT_REGION) \
		-e AWS_ACCESS_KEY_ID \
		-e AWS_SECRET_ACCESS_KEY \
		-e AWS_SESSION_TOKEN \
		-e prefix=$(prefix) \
		-e account_name=$(account_name) \
		-e aws_env=$(aws_env)

deploy-burger-cf-in-docker: build-docker-image ## deploy burger in docker
	@docker run -i \
		-v $(PWD):/data \
		-e AWS_ACCESS_KEY_ID \
		-e AWS_SECRET_ACCESS_KEY \
		-e AWS_SESSION_TOKEN \
		-e AWS_DEFAULT_REGION=$(AWS_DEFAULT_REGION) \
		-e prefix=$(prefix) \
		-e account_name=$(account_name) \
		-e aws_env=$(aws_env) \
		$(DOCKER_IMAGE) \
		/bin/bash -c "make deploy-burger-cf"
