# Thermal Store Controller

This is MicroPython code that is designed to monitor and control a thermal store. It will:

- Measure the temperature at different levels in the tank
- Control an immersion heater based on the battery level
- Enable or disable the thermostat control for a gas boiler

It is designed to work in a system that has Lithium Ion batteries connected to a Victron inverter charger and uses MQTT to get the current state of charge of the batteries as well as outputting the current status of the system.

## To Do:

- [ ] Update settings via MQTT
- [ ] NTP Clock sync
- [ ] Settings based on time of year
- [x] MQTT Output on change
- [x] Persistent settings
