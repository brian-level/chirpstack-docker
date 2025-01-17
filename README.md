# ChirpStack Docker For LoRaWan Ping/Pong testing

This repository contains a setup [ChirpStack](https://www.chirpstack.io)
open-source LoRaWAN Network Server stack using [Docker Compose](https://docs.docker.com/compose/).

## Directory layout

* `buildponger.sh`: a script to build the local ponger application docker image
* `docker-compose.yml`: the docker-compose file containing the services
* `docker-compose-env.yml`: alternate docker-compose file using environment variables, can be run with the docker-compose `-f` flag
* `configuration/chirpstack*`: directory containing the ChirpStack configuration files, see:
    * https://www.chirpstack.io/gateway-bridge/install/config/
    * https://www.chirpstack.io/network-server/install/config/
    * https://www.chirpstack.io/application-server/install/config/
* `configuration/postgresql/initdb/`: directory containing PostgreSQL initialization scripts
* `python/`: directory containing python used for the ponging application

## Initial Setup

You should run the buildponger script first to create the application / http integration docker
Note that this might take quite a while as it needs to build some python packages

```
./buildponger
```

## Configuration

The ChirpStack stack components components are pre-configured to work with the provided
`docker-compose.yml` file

# Data persistence

PostgreSQL and Redis data is persisted in Docker volumes, see the `docker-compose.yml`
`volumes` definition.

## Requirements

Before using this `docker-compose.yml` file, make sure you have [Docker](https://www.docker.com/community-edition)
installed.

## Usage

To start the ChirpStack open-source LoRaWAN Network Server stack, simply run:

```bash
$ docker-compose up
```

**Note:** during the startup of services, it is normal to see the following errors:

* ping database error, will retry in 2s: dial tcp 172.20.0.4:5432: connect: connection refused
* ping database error, will retry in 2s: pq: the database system is starting up


After all the components have been initialized and started, you should be able
to open http://localhost:8080/ in your browser.

### Add Network Server

When adding the Network Server in the ChirpStack Application Server web-interface
(see [Network Servers](https://www.chirpstack.io/application-server/use/network-servers/)),
you must enter `chirpstack-network-server:8000` as the Network Server `hostname:IP`.

