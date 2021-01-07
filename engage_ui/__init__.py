#
# Copyright 2019-2020 VMware, Inc.
#
# SPDX-License-Identifier: BSD-2-Clause
#
"""
People Counter engage microservice to display data analyzed by the inference microservice 

"""

from flask_socketio import SocketIO, emit
from flask import Flask
import logging

format = "%(asctime)s - %(levelname)s: %(threadName)s - %(message)s"
logging.basicConfig(format=format, level=logging.DEBUG,
                        datefmt="%H:%M:%S")

__author__ = 'pseassistance@vmware.com'

socketio = None

def create_app():
    global socketio
    app = Flask(__name__, instance_relative_config=True)

    # Load the default configuration
    app.config.from_object('config.default')

    # Load the configuration from the instance folder
    app.config.from_pyfile('config.py')

    # Load the file specified by the APP_CONFIG_FILE environment variable
    # Variables defined here will override those in the default configuration
    app.config.from_envvar('APP_CONFIG_FILE')

    # Wrap the python application with socket.io
    socketio = SocketIO(app, async_mode=None, logger=True, engineio_logger=True)

    # Import routes
    from . import views

    app.register_blueprint(views.root)
    
    return app

def run_app():
    app = create_app()
    socketio.run(app, host="0.0.0.0")