.PHONY: init # Init local environemnt
init: 
	pdm install

.PHONY: upcounter # Build RTLIL for the design
upcounter:
	CHIPFLOW_ROOT=upcounter pdm run chipflow silicon prepare

.PHONY: upcounter_clean # Clean/delete the builds
upcounter_clean: 
	rm -fr upcounter/build

.PHONY: fibonacci # Build RTLIL for the design
fibonacci:
	CHIPFLOW_ROOT=fibonacci pdm run chipflow silicon prepare

.PHONY: fibonacci_clean # Clean/delete the builds
fibonacci_clean: 
	rm -fr fibonacci/build

.PHONY: rom # Build RTLIL for the design
rom:
	CHIPFLOW_ROOT=rom pdm run chipflow silicon prepare

.PHONY: rom_clean # Clean/delete the builds
rom_clean: 
	rm -fr rom/build

.PHONY: clean # Clean/delete the builds
clean: upcounter_clean fibonacci_clean

.PHONY: lint # Lint code
lint: 
	pdm run lint
