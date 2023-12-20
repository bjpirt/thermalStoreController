.PHONY: start-mosquitto
start-mosquitto:
	docker run -d --name mosquitto -p 1883:1883 -v ${PWD}/mosquitto/mosquitto.conf:/mosquitto/config/mosquitto.conf eclipse-mosquitto

.PHONY: stop-mosquitto
stop-mosquitto:
	docker stop mosquitto

.PHONY: upload
upload:
	ampy put initial_config.py
	ampy put config.py
	ampy put hardware_gateway_impl.py
	ampy put hardware_gateway.py
	ampy put occupancy_impl.py
	ampy put occupancy.py
	ampy put mqtt_gateway_impl.py
	ampy put mqtt_gateway.py
	ampy put temperature_sensor.py
	ampy put thermal_store_controller.py
	ampy put timeout.py
	ampy put main.py

.PHONY: test
test:
	python -m unittest --verbose
