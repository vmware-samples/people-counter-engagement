#
# Copyright 2019-2020 VMware, Inc.
#
# SPDX-License-Identifier: BSD-2-Clause
#
import threading
import base64
import os
from . import socketio
import logging
from queue import Queue
import sys
from time import sleep
import signal
import paho.mqtt.client as mqtt
from object_store.providers.minio_object_store import MinioObjectStore as store
import json

class FileDownloadManager():
    def __init__(self,  
        mqtt_args, 
        object_store_args,
        download_folder = '/tmp',
        file_cache_size = 10,
        file_cleanup_interval_sec = 10,
        file_download_interval_min = 1
        ):
        # Initialization function which parses command-line arguments from the user as well as set defaults

         # Variables needed for the internal mechanisms of the class
        self.folder_lock = threading.RLock()
        self.mqtt_client = mqtt.Client()
        self.mqtt_qos_level = 0
        self.mqtt_client_connection_error = ""
        self.download_queue = Queue()
        self.display_map = {}
        self.updates_queue = Queue()
        self.deletion_queue = Queue()
        self.image_serving_folder = 'static/images/'

        # Assign event callbacks for MQTT client
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_disconnect = self.on_disconnect
        self.mqtt_client.on_message = self.on_message

        # Assign arguments passed on to the function to class variables and validate
        self.mqtt_args = mqtt_args
        self.object_store_args = object_store_args
        self.download_folder = download_folder
        self.file_cache_size = file_cache_size
        self.file_cleanup_interval_sec = file_cleanup_interval_sec
        self.file_download_interval_min = file_download_interval_min
        self.validate()
        
        # Initialize object store connection
        self.object_store = store()
        self.object_store.initialize(self.object_store_args)

        # Initialize the MQTT client connection
        logging.info("Connecting to MQTT broker...")
        self.mqtt_client.username_pw_set(self.mqtt_args['username'], self.mqtt_args['password'])
        self.mqtt_client.connect(self.mqtt_args['hostname'], self.mqtt_args['port'])
        self.mqtt_client.loop_start()
        sleep(5)
        if self.mqtt_client_connection_error != "":
            raise Exception(self.mqtt_client_connection_error)
        logging.info("Success")
        logging.info("Subscribing to topic {0}...".format(self.mqtt_args['topic']))
        self.mqtt_client.subscribe(self.mqtt_args['topic'])
    
    def validate(self):
        # This function does validation of the command-line arguments

        if not os.access(self.download_folder, os.F_OK):
            raise Exception("The folder ({0}) specified for image storage does not exist"
                .format(self.download_folder))
        if not os.access(self.download_folder, os.R_OK):
            raise Exception("The folder ({0}) specified for image storage is not readable"
                .format(self.download_folder))
        if not os.access(self.download_folder, os.X_OK):
            raise Exception("The folder ({0}) specified for image storage does not have execute permissions"
                .format(self.download_folder))
        if not os.access(self.download_folder, os.W_OK):
            raise Exception("The folder ({0}) specified for image storage is not writtable"
                .format(self.download_folder))
        if self.file_cache_size <= 1:
            raise Exception("The number of images to keep on disk must be at least 2. Value given: {0}"
                .format(self.file_cache_size))
        if self.file_cleanup_interval_sec <= 0:
            raise Exception("The interval to clean up images must be a number greater than 0. Value given: {0}"
                .format(self.file_cleanup_interval_sec))
        if self.file_download_interval_min <= 0:
            raise Exception("The interval to check for new images to download must be a number greater than 0. Value given: {0}"
                .format(self.file_download_interval_min))

    # Define event callbacks for MQTT client
    def on_connect(self, client, userdata, flags, rc):
        logging.debug("Connected with result code: " + str(rc))
        if rc != 0 and rc != 3:
            self.mqtt_client_connection_error = "Connection to MQTT broker failed with error code: {0}".format(str(rc))

    # Define event callback for disconnect
    def on_disconnect(self, client, userdata, rc):
        logging.info("Disconnecting from MQTT")

    ### 
    ### Algorithm to accommodate for multiple devices producing data
    ### and multiple compute nodes consuming this data for inference.
    ###
    def on_message(self, client, obj, msg):
        logging.debug(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

        ## TODO add error handling
        msg_payload = json.loads(msg.payload)
        self.save_metadata(msg_payload)
       
    #TODO Change message to provide status of image before it is selected.
    #TODO Change the internal data structure that hold images from queue to a map
    # where an entry in the map is map[deviceID] == {device metadata}
    def save_metadata(self, msg_payload):
        if msg_payload['type'] == "result":
            self.download_queue.put(msg_payload)

    # This function downloads images
    def start_downloads(self):
        logging.info("Starting the download thread")
        logging.info("Downloading files to folder %s...", self.download_folder)
        while True:
            #   block on read from queue
            #       download image and place in folder
            try:
                msg_payload = self.download_queue.get(block=True)                
            except Exception as e:
                # This is an error and shouldn't occur. We're blocking till we get an item
                logging.debug("Download queue error %s", str(e))
                continue
            
            logging.debug("Received message payload from download queue. Message: %s", str(msg_payload))
            image_path = msg_payload['filePath']
            tokenized_image_path = image_path.split("/")
            bucket_name = tokenized_image_path[0]
            filename = tokenized_image_path[1]
            download_path = os.path.join(self.download_folder, filename)

            try:
                self.object_store.download(filename, download_path, bucket_name)
            except Exception as e:
                logging.error("An error occurred that prevented the download of the file '%s'. Error: %s", filename, str(e))
                continue
            
            msg_payload['downloadPath'] = download_path
            msg_payload['displayPath'] = self.image_serving_folder + filename
            if msg_payload['deviceID'] in self.display_map:
                self.deletion_queue.put(self.display_map[msg_payload['deviceID']])
            self.display_map[msg_payload['deviceID']] = msg_payload
            self.updates_queue.put(msg_payload)

    def start_cleanup(self):
        logging.info("Starting the cleanup thread")
        logging.info("File cleanup interval set to %d second(s)", self.file_cleanup_interval_sec)
        while True:
            try:
                file_metadata = self.deletion_queue.get(block=True)
            except Exception as e:
                continue

            logging.debug("Deleting file: %s from the filesystem", file_metadata['downloadPath'])
            try:
                os.remove(file_metadata['downloadPath'])
            except Exception as e:
                logging.error("An error occurred that prevented the deletion of the file ({0}) in the image folder. Error: {1}".format(file_metadata['downloadPath'], str(e)))

    # Get all device information
    def get_all_devices(self):
        return self.display_map

    # Stream updates from devices
    def publish_devices_updates(self):
        logging.info("Starting the publishing thread")
        while True:
            #   block on read from queue to publish updates
            try:
                payload = self.updates_queue.get(block=True)                
            except Exception as e:
                # This is an error and shouldn't occur. We're blocking till we get an item
                logging.debug("Updates queue error %s", str(e))
                continue
            socketio.emit('devicesupdates', payload, namespace='/test')

    def run(self):
        # Start all the threads
        download_thread = threading.Thread(target=self.start_downloads, name='DownloadThread', daemon=True)
        download_thread.start()
        publish_thread = threading.Thread(target=self.publish_devices_updates, name='PublishThread', daemon=True)
        publish_thread.start()
        cleanup_thread = threading.Thread(target=self.start_cleanup, name='CleanupThread', daemon=True)
        cleanup_thread.start()
        logging.debug('All threads initialized')