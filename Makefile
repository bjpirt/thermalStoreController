.PHONY: start-mosquitto
start-mosquitto:
	docker run -d --name mosquitto -p 1883:1883 -v ${PWD}/mosquitto/mosquitto.conf:/mosquitto/config/mosquitto.conf eclipse-mosquitto

.PHONY: stop-mosquitto
stop-mosquitto:
	docker stop mosquitto

.PHONY: upload
upload:
	ampy put config.py
	ampy put main.py
	ampy put mqtt_connection.py
	ampy put temperature_sensor.py
	ampy put thermal_store_controller.py
	ampy put timeout.py
