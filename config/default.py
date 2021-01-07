#
# Copyright 2019-2020 VMware, Inc.
#
# SPDX-License-Identifier: BSD-2-Clause
#
# Flask configurations
DEBUG = False
SECRET_KEY = 'some-secret!' # This is insecure and should be override it in your instance/config.py file 

# Application configurations
# All the configurations that have CHANGE_ME should be overritten in the instance/config.py file
# and not committed to source control
MQTT_USERNAME = "CHANGE_ME"
MQTT_PASSWORD = "CHANGE_ME"
MQTT_HOSTNAME = "CHANGE_ME"
MQTT_PORT = 1883
MQTT_TOPIC = "image/latest"
OBJECT_STORE_HOSTNAME = "CHANGE_ME"
OBJECT_STORE_ACCESS_KEY = "CHANGE_ME"
OBJECT_STORE_SECRET_KEY = "CHANGE_ME"
OBJECT_STORE_PORT = 9000
OBJECT_STORE_HTTPS_ENABLED = True
IMAGE_CACHE_DIRECTORY = "/var/lib/people-counter-ingestion"