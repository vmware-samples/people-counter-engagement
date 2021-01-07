# people-counter-engagement

Engagement service for the People Counter Demo application. It is written in Python and displays images on an interval from the Raspberry Pi 3 Camera. The daemon uses MQTT and MinIO to get the photos.

## Prerequisites

The following needs to be installed on the machine that is going to be running the microservice:

* Docker

You must have access to the following services from the machine running the microservice:

* MQTT
* MinIO

## Development Environment Setup

The microservice has some Python and NodeJS dependencies. The prerequisites to get your development environment up and running are:

* Python 3.6.9
* pip 20.0.2
* NodeJS 14.0.0
* npm 6.14.4

Once you have the dependencies installed in your development environment, run the following commands from the root directory of the project:

```bash
pip install -r requirements.txt
cd engage_ui/static
npm install
```

What the commands above do is install all the dependency of the application.

## Configuration

You need to be provided configurations in order to run the app. The configurations are sensitive information and environment dependent which is why they are not included in the [config/default.py](config/default.py) file. To provide the information, create the folder `instance` in the root directory of the project. Inside the folder, create the file `config.py`. The content of the file should be:

```python
# Flask configurations
DEBUG = False
SECRET_KEY = "CHANGE_ME" # This is insecure and should be override it in your instance/config.py file 

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
IMAGE_CACHE_DIRECTORY = "engage_ui/static/images"
```

Substitute `CHANGE_ME` with your environment information.

In the requirements.txt file, add the People Counter Library repo as a dependency. E-mail the authors for more information on how to do that.

## Build

There is a Dockerfile that comes with the project which can be used to build a Docker image. To build the image, run the following command from the root directory of the project:

```bash
docker build --tag people-counter-engage .
```

After it completes, you will have a Docker image that can be used to deploy the application.

## Run

Copy the Docker image you built earlier into the target Linux system you want to use to run the microservice. Afterwards, start up the service with the following command:

```bash
docker run -d --env APP_CONFIG_FILE=/app/instance/config.py -p 5000:5000 --name engage-test people-counter-engagement
```

Once the command finishes execution, the People Counter Engage UI will be available. To test the UI works, open up a browser and if you are running the image locally in your laptop, type the address `http://localhost:5000/`. You should see the UI come up after a short delay. If you are running the image somewhere other than your laptop, make sure to substitude `localhost` for whatever the IP or hostname is for the host running the code.

## Contributing

The people-counter-engagement project team welcomes contributions from the community. Before you start working with people-counter-engagement, please
read our [Developer Certificate of Origin](https://cla.vmware.com/dco). All contributions to this repository must be
signed as described on that page. Your signature certifies that you wrote the patch or have the right to pass it on
as an open-source patch. For more detailed information, refer to [CONTRIBUTING.md](CONTRIBUTING.md).

## Authors

* [Luis M. Valerio](https://github.com/lvalerio)
* [Neeraj Arora](https://github.com/nearora)

## License

This project is licensed under the BSD 2-Clause License - see the [LICENSE.txt](LICENSE.txt) file for details
