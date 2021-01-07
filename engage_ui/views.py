#
# Copyright 2019-2020 VMware, Inc.
#
# SPDX-License-Identifier: BSD-2-Clause
#
from flask_socketio import SocketIO, emit
from flask import Flask, jsonify, render_template, url_for, copy_current_request_context, Blueprint, current_app, session
from . import socketio, models

root = Blueprint('root', __name__)
download_manager = None

@root.route('/')
def index():
    global download_manager
    # Render index page
    if not download_manager:
        app = current_app
         # Get MQTT configurations
        mqtt_args = {
            "username": app.config["MQTT_USERNAME"],
            "password": app.config["MQTT_PASSWORD"],
            "hostname": app.config["MQTT_HOSTNAME"],
            "port": app.config["MQTT_PORT"],
            "topic": app.config["MQTT_TOPIC"]
        }

        # Get object store configurations
        object_store_args = {
            "host": app.config["OBJECT_STORE_HOSTNAME"] + ":" + str(app.config["OBJECT_STORE_PORT"]),
            "accessKey": app.config["OBJECT_STORE_ACCESS_KEY"],
            "secretKey": app.config["OBJECT_STORE_SECRET_KEY"],
            "httpsEnabled": app.config["OBJECT_STORE_HTTPS_ENABLED"]
        }
        
        # Initialize and run download manager
        download_manager = models.FileDownloadManager(
            mqtt_args, 
            object_store_args,
            download_folder=app.config["IMAGE_CACHE_DIRECTORY"]
        )
        download_manager.run()
    current_app.logger.debug("In the index function")
    return render_template('index.html')

@socketio.on('connect', namespace='/test')
def test_connect():
    current_app.logger.info('Client connected')

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    current_app.logger.info('Client disconnected')

@root.route('/api/v1.0/devices', methods=['GET'])
def get_devices():
    global download_manager
    return jsonify(download_manager.get_all_devices())