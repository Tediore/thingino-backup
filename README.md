# Thingino auto-backup tool

A simple tool to automatically (or once) fetch configuration backups from your Thingino devices. If auto-backup is enabled, it will run every night at midnight.

<br>

# Configuration
Configuration takes place within a YAML file (config.yaml).
```yaml
auto_backup: # Optional. Defaults to false if not in configuration. Will run once and stop if set to false.
  max_backups: 1 # Required if using auto-backup. Maximum number of backups to keep.

log_level: debug # Optional. Valid options are `debug`, `info`, `warning`, and `error`. Defaults to `info`.

devices: # Required.
  Alley camera: # Required. Arbitrary name for the device.
    hostname: alley-cam.lan # Required. Hostname or IP address of the Thingino device.
    password: 5up3r-53cur3-p455w0rd # Required. Root password of the Thingino device.

  Front door camera:
    hostname: front-door-cam.lan
    password: hunter2
```

<br>

# How to run

**Docker via `docker-compose`**

1. Create your docker-compose.yaml (or add to existing). Example docker-compose.yaml:
```yaml
version: '3.7'
services:
  thingino-backup:
    image: tediore/thingino-backup:stable
    container_name: thingino-backup
    restart: 'unless-stopped'
    volumes:
    - /opt/thingino:/thingino # config.yaml must be located in whatever directory you map to /thingino (in this example, /opt/thingino/config.yaml)
    - /etc/localtime:/etc/localtime:ro # Optional, but ensures backups occur at local time
```
2. `docker-compose up -d thingino-backup`

<br>

**Docker via `docker run`**

Example `docker run` command:
```
docker run --name thingino-backup \
-v /opt/thingino:/thingino \
-v /etc/localtime:/etc/localtime:ro \
tediore/thingino-backup:stable
```