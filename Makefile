# Setting SHELL to bash allows bash commands to be executed by recipes.
# Options are set to exit when a recipe line exits non-zero or a piped command fails.
SHELL = /usr/bin/env bash -o pipefail
.SHELLFLAGS = -ec

VERSION ?= $(shell git describe --dirty --tags --match='v*' 2>/dev/null || git rev-parse --short HEAD)
REGISTRY ?= ghcr.io
REPO ?= stackitcloud/grafana-backup-tool
PLATFORMS ?= amd64 arm64

.PHONY: all
all: verify

##@ Build

build:
	@poetry install

.PHONY: image
image: ## Build Docker image.
	docker buildx build \
		--output type=image,name=$(REGISTRY)/$(REPO),push=false \
		--platform $(PLATFORMS) \
		--tag $(REGISTRY)/$(REPO):$(VERSION) \
		--file Dockerfile .

.PHONY: push
push: image ## Build and push Docker image.
	docker push $(REGISTRY)/$(REPO):$(VERSION)

.PHONY: buildx-and-push
buildx-and-push: ## Build multi-platform and push Docker image.
	docker buildx build \
		--output type=image,name=$(REGISTRY)/$(REPO),push=true \
		--platform $(PLATFORMS) \
		--tag $(REGISTRY)/$(REPO):$(VERSION) \
		--file Dockerfile .

##@ Python

.PHONY: fmt
fmt: ## Run ruff format and ruff sort imports.
	@poetry run ruff format .
	@poetry run ruff check --select I --fix .

.PHONY: lint
lint: ## Run ruff linter.
	@poetry run ruff check .

.PHONY: check
check: lint fmt ## Run Python checks (lint + format).

.PHONY: test
test: ## Run tests with pytest.
	@poetry run pytest

.PHONY: test-cover
test-cover: ## Run tests with coverage.
	@poetry run pytest --cov=grafana_backup --cov-report=html

##@ Verification

.PHONY: verify-fmt
verify-fmt: fmt ## Verify Python code is formatted.
	@if !(git diff --quiet HEAD); then \
		echo "unformatted files detected, please run 'make fmt'"; exit 1; \
	fi

.PHONY: verify
verify: verify-fmt check

##@ Maintenance

.PHONY: clean
clean: ## Remove build artifacts.
	rm -rf dist/ build/ *.egg-info grafana_backup.egg-info
	rm -rf .pytest_cache/ .coverage cover.html
	rm -rf htmlcov/

.PHONY: help
help: ## Display this help.
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)
