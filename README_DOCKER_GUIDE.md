# Deploy Details
This is guide to all the steps I use to deploy the app, so that I don't forget anything.

### 1. Add missing configuration info and asset data

There are various files that I'm using that aren't in the github. These include
```
hello/config.py                                # config.py.example can be used as an example
secrets/<certificate_for_database>.pem         # The location of this file can be set in the config.py file
hello/static/place_img/<location_slug>.png     # Each location needs an image
hello/static/place_img/sad_panda_400x400.jpeg  # The name of this image is currently hardcoded in
hello/static/place_img/dangan_map_404.jpg      # Another hardcoded image name
```

### 2. Build the image
I'm using my juncothebird account on dockerhub to manage the images.

```sh
docker build -t juncothebird/qrest .
```
After that I push the build using docker for Windows.

### 3. Setup nginx proxy manager
Create a new directory for NPM then use a docker-compose to create the container.
```sh
cd /opt
mkdir nginxproxymanager
cd nginxproxymanager
```
Create a file `docker-compose.yaml`:
```yaml
services:
  app:
    image: 'jc21/nginx-proxy-manager:latest'
    restart: unless-stopped
    ports:
      # These ports are in format <host-port>:<container-port>
      - '80:80'   # Public HTTP Port
      - '443:443' # Public HTTPS Port
      - '81:81'   # Admin Web Port

    volumes:
      - ./data:/data
      - ./letsencrypt:/etc/letsencrypt
```

Then:
```sh
docker compose up -d
```
Login to the admin page at `<your_ip_address>:81` using
```
email:    admin@example.com
password: changeme
```

### 4. Setup server and pull image
I'm hosting on DigitalOcean using "Docker on Ubuntu 22.04"
```sh
docker login
docker pull juncothebird/qrest
docker run -d --network nginx-proxy-manager_default --name=qrest-container juncothebird/qrest
```
Note that `nginx-proxy-manager_default` is the default network name created by NPM, but it could be different.

You'll want to setup setup NPM to forward traffic to the address `qrest-container`.

### 5. WHITELIST THE IP OF THE SERVER ON MONGODB.COM
I always forget this step