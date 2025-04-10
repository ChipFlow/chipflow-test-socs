.PHONY: init # Init local environemnt
init: 
	pdm install

.PHONY: clean # Clean/delete the builds

define soc_target
.PHONY: $(1) # Build RTLIL for the design
$(strip $(1))/pins.lock:
	@CHIPFLOW_ROOT=$(strip $(1)) PYTHONPATH=$PYTHONPATH:${PWD} pdm run chipflow pin lock

$(1): $(strip $(1))/pins.lock
	@CHIPFLOW_ROOT=$(strip $(1)) PYTHONPATH=$PYTHONPATH:${PWD} pdm run chipflow silicon prepare

.PHONY: $(1)_submit # Submit RTLIL for build
$(1)_submit: $(1)
	@CHIPFLOW_ROOT=$(strip $(1)) PYTHONPATH=$PYTHONPATH:${PWD} pdm run chipflow silicon submit

.PHONY: $(1)_clean # clean the design
$(1)_clean:
	rm -fr $(strip $(1))/build

.PHONY: $(1)_lint
$(1)_lint:
	cd $(strip $(1))/design && pdm run lint

clean: $(1)_clean
endef

$(eval $(call soc_target, upcounter))
$(eval $(call soc_target, rom))
$(eval $(call soc_target, sram))

.PHONY: lint # Lint code
lint: 
	pdm run lint
