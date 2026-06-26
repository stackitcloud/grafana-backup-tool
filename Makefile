# Setting SHELL to bash allows bash commands to be executed by recipes.
# Options are set to exit when a recipe line exits non-zero or a piped command fails.
SHELL = /usr/bin/env bash -o pipefail
.SHELLFLAGS = -ec

VERSION ?= $(shell git describe --dirty --tags --match='v*' 2>/dev/null || git rev-parse --short HEAD)
MELANGE_VERSION ?= $(patsubst v%,%,$(word 1,$(subst -, ,$(VERSION))))
REGISTRY ?= ghcr.io
REPO ?= stackitcloud/grafana-backup-tool
PLATFORMS ?= amd64
MELANGE_KEY ?= melange.rsa
PACKAGES_DIR ?= packages
IMAGE_TAG ?= $(REGISTRY)/$(REPO):$(VERSION)
IMAGE_TAR ?= grafana-backup-tool.tar
LOCAL ?= false

.PHONY: all
all: verify

##@ Build

build:
	poetry install

.PHONY: key
key: ## Generate melange signing key.
	@test -f $(MELANGE_KEY) || melange keygen $(MELANGE_KEY)

.PHONY: melange-build
melange-build: key ## Build APK package with melange.
	sed 's/^  version:.*/  version: $(MELANGE_VERSION)/' melange.yaml > .melange.yaml
	@for arch in $$(echo $(PLATFORMS) | tr ',' ' '); do \
		echo "Building architecture: $$arch"; \
		melange build .melange.yaml \
			--source-dir . \
			--out-dir $(PACKAGES_DIR) \
			--arch $$arch \
			--signing-key $(MELANGE_KEY); \
	done
	rm -f .melange.yaml

.PHONY: image
image: melange-build ## Build OCI image. Set LOCAL=true to load to local Docker, false (default) to push.
ifeq ($(LOCAL),true)
	@echo "Building image locally and loading into Docker..."
	apko build apko.yaml \
		$(IMAGE_TAG) \
		$(IMAGE_TAR) \
		--sbom=false \
		--arch $(PLATFORMS) \
		-r "@local ./$(PACKAGES_DIR)" \
		--keyring-append $(MELANGE_KEY).pub
	docker load -i $(IMAGE_TAR)
else
	@echo "Publishing image to registry $(REGISTRY)..."
	apko publish apko.yaml \
		$(IMAGE_TAG) \
		--sbom=false \
		--arch $(PLATFORMS) \
		-r "@local ./$(PACKAGES_DIR)" \
		--keyring-append $(MELANGE_KEY).pub
endif

##@ Python

.PHONY: fmt
fmt: ## Run ruff format and ruff sort imports.
	poetry run ruff format .
	poetry run ruff check --select I --fix .

.PHONY: lint
lint: ## Run ruff linter.
	poetry run ruff check .

.PHONY: check
check: lint test ## Run Python checks.

.PHONY: test
test: ## Run tests with pytest.
	poetry run pytest

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
	rm -rf .pytest_cache/ .coverage coverage.xml
	rm -rf $(PACKAGES_DIR)/ .melange.yaml $(IMAGE_TAR)

.PHONY: help
help: ## Display this help.
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)
