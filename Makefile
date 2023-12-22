.PHONY: start-mosquitto
start-mosquitto:
	docker run -d --name mosquitto -p 1883:1883 -v ${PWD}/mosquitto/mosquitto.conf:/mosquitto/config/mosquitto.conf eclipse-mosquitto

.PHONY: stop-mosquitto
stop-mosquitto:
	docker stop mosquitto

.PHONY: upload
upload:
	ampy put hardware
	ampy put lib
	ampy put mqtt
	ampy put thermal_store_controller
	ampy put config.py
	ampy put initial_config.py
	ampy put main.py
	ampy put stubs/typing.py typing.py

.PHONY: test
test:
	python -m unittest --verbose

.PHONY: lint
lint:
	pylint --recursive=y ./**/*.py

.PHONY: ruff
ruff:
	ruff check .

.PHONY: mypy
mypy:
	mypy --exclude scripts --exclude test --exclude stubs --check-untyped-defs .

.PHONY: check
check: lint ruff mypy
