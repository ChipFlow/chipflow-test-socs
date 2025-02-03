.PHONY: init # Init local environemnt
init: 
	pdm install

.PHONY: upcounter # Build RTLIL for the design
upcounter:
	CHIPFLOW_ROOT=upcounter pdm run chipflow silicon prepare

.PHONY: upcounter_clean # Clean/delete the builds
upcounter_clean: 
	rm -fr upcounter/build

.PHONY: rom # Build RTLIL for the design
rom:
	CHIPFLOW_ROOT=rom pdm run chipflow silicon prepare

.PHONY: rom_clean # Clean/delete the builds
rom_clean: 
	rm -fr rom/build

.PHONY: clean # Clean/delete the builds
clean: upcounter_clean fibonacci_clean rom_clean sram_clean

.PHONY: lint # Lint code
lint: 
	pdm run lint
