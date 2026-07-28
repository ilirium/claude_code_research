# Claude Code research repo.
#
# Python work runs against the shared uv-managed venv, overridable:
#     make validate VENV=~/Dev/uv/envs/other

VENV        ?= $(HOME)/Dev/uv/envs/dev
PYTHON      := $(VENV)/bin/python
UV_PYTHON   ?= 3.14.6
AGENTS_DIR  ?= agents
VALIDATOR   := $(AGENTS_DIR)/scripts/validate-frontmatter.py

.DEFAULT_GOAL := help
.PHONY: help validate validate-uv env env-clean

help: ## Show this help
	@grep -hE '^[a-z-]+:.*?## ' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'
	@echo
	@echo "  venv: $(VENV)"

validate: | check-venv ## Validate agent frontmatter using the shared venv
	@$(PYTHON) $(VALIDATOR) $(AGENTS_DIR)

validate-uv: ## Same check with no venv at all (uv resolves deps from the script header)
	@uv run $(VALIDATOR) $(AGENTS_DIR)

env: ## Create or repair the shared venv and its dependencies
	@uv venv --python $(UV_PYTHON) $(VENV)
	@VIRTUAL_ENV=$(VENV) uv pip install pyyaml
	@$(PYTHON) --version

env-clean: ## Delete the shared venv
	@rm -rf $(VENV)
	@echo "removed $(VENV)"

check-venv:
	@test -x $(PYTHON) || { \
		echo "No interpreter at $(PYTHON)."; \
		echo "Run 'make env' to create it, or 'make validate-uv' to skip the venv entirely."; \
		exit 1; \
	}
