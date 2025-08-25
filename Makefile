REPO_URL ?= reg3.infra.ske.eu01.stackit.cloud
DOCKER_REPO ?= stackitcloud
DOCKER_NAME := grafana-backup-tool
DOCKER_TAG ?= v1.4.2-ske-1
PLATFORMS ?= linux/amd64

FULLTAG = $(REPO_URL)/$(DOCKER_REPO)/$(DOCKER_NAME):$(DOCKER_TAG)

DOCKERFILE=Dockerfile

all: build

build:
	docker build -t $(FULLTAG) -f $(DOCKERFILE) .

push: build
	docker push $(FULLTAG)


buildx_and_push:
	docker buildx build \
		--output type=image,name=$(DOCKER_REPO)/$(DOCKER_NAME),push=true \
	 	--platform $(PLATFORMS) \
		--tag $(FULLTAG) \
	 	--file $(DOCKERFILE) .
