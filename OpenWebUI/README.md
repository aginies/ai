# OpenWebUI Systemd Service Setup

This guide provides a step-by-step process for setting up an **open-webui** container as a systemd service. This approach is useful when you want your container to start automatically at boot and be managed through systemd commands.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Steps to Create a Systemd Service](#steps-to-create-a-systemd-service)
  - [1. Define the Systemd Unit File](#1-define-the-systemd-unit-file)
  - [2. Create the podman Volume](#2-create-the-podman-volume)
  - [3. Reload and Enable the Systemd Service](#3-reload-and-enable-the-systemd-service)
  - [4. Start the Service](#4-start-the-service)
  - [5. Verify the Status](#5-verify-the-status)
- [Managing the Service](#managing-the-service)
- [Notes](#notes)

## Prerequisites

Before starting, ensure you have:

- **podman** installed and running on your system.
- Sufficient privileges (sudo or root) to create systemd service files and manage Docker volumes.
- Ensure Docker is enabled and managed by systemd.

## Steps to Create a Systemd Service

### 1. Define the Systemd Unit File

Create a new file named `open-webui.service` in `/etc/systemd/system/`. Adjust the value to your needs, especially the volume.

```bash
# vi /etc/systemd/system/open-webui.service
[Unit]
Description=OpenWebUI
After=network-online.target,nginx.service,ollama.service
Requires=nginx.service,ollama.service

[Service]
Restart=always
# Adjust to your path to store all data and models
Environment=DATADIR=/mnt/data/openwebui/data:/app/backend/data
Environment=IPADDR_OLLAMA=10.0.1.38
Environment=IPADDR_COMFYUI=10.0.1.38
ExecStop=/usr/bin/podman stop -t 2 open-webui

ExecStartPre=-/usr/bin/podman rm -f open-webui
# https://docs.openwebui.com/getting-started/advanced-topics/env-configuration/#security-variables
ExecStart=/bin/sh -c 'podman run --rm --name=open-webui \
    -p 3000:3000 \
    -v ${DATADIR} \
    -e ENABLE_SIGNUP=false \
    -e WEBUI_AUTH=false \
    -e CORS_ALLOW_ORIGIN=* \
    -e ENABLE_COMMUNITY_SHARING=false \
    -e ENABLE_EVALUATION_ARENA_MODELS=false \
    -e ENABLE_CHANNELS=false \
    -e GLOBAL_LOG_LEVEL="DEBUG" \
    -e ENABLE_MESSAGE_RATING=false \
    -e OLLAMA_BASE_URL=http://${IPADDR_OLLAMA}:11434 \
    -e ENABLE_OPENAI_API=false \
    -e DEFAULT_LOCALE=fr \
    -e PORT=3000 \
    -e COMFYUI_BASE_URL=http://${IPADDR_COMFYUI}:8188 \
    -e ENABLE_IMAGE_GENERATION=true \
    -e IMAGE_GENERATION_ENGINE=comfyui \
    -e IMAGE_GENERATION_MODEL=cyberrealistic_v41BackToBasics.safetensors \
    -e IMAGE_SIZE=512x288 \
    -e IMAGE_STEPS=45 \
    ghcr.io/open-webui/open-webui:main'

RestartSec=30
TimeoutStopSec=70
#WatchdogSec=60

[Install]
WantedBy=multi-user.target default.target
```

### 2. Create the podman Volume 

Create a volume named open-webui before starting the service: 
```bash
# podman volume create open-webui
```
 
### 3. Reload and Enable the Systemd Service 

Inform systemd about the new service and enable it to start at boot: 
```bash
# sudo systemctl daemon-reload
# sudo systemctl enable open-webui.service
```
 
### 4. Start the Service 

Begin the open-webui service using the following command: 
```bash
# sudo systemctl start open-webui.service
```
 
### 5. Verify the Status 

Confirm that the service is running correctly: 
```bash
# sudo systemctl status open-webui.service
```

## Nginx and https

Why https? Its of course more secure, but also add the microphone feature to directly ask a question without any keyboard :)
All the [documentation](https://docs.openwebui.com/tutorials/integrations/https-nginx/) is on the official website. You can also run nginx on your server without any container, just put the `open-webui.conf` in `/etc/nginx/conf.d/` directory and restart your nginx service.

Example of my configuration for an IP address of 10.0.1.38:
```configuration
server {
    listen 443 ssl;
    server_name 10.0.1.38;

    ssl_certificate /etc/nginx/ssl/nginx.crt;
    ssl_certificate_key /etc/nginx/ssl/nginx.key;
    ssl_protocols TLSv1.2 TLSv1.3;

    location / {
        proxy_pass http://10.0.1.38:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

	proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_buffering off;
    }
}
server {
    listen 80;
    server_name 10.0.1.38;

    return 301 https://$host$request_uri;
    location ~ /.well-known/acme-challenge { allow all; }
}
```

Now just connect to https://YOURIP and you should be on the **open-webui** frontend.

## Managing the Service

- Start : sudo systemctl start open-webui.service
- Stop : sudo systemctl stop open-webui.service
- Restart : sudo systemctl restart open-webui.service
- Status : sudo systemctl status open-webui.service
     

## Notes 

- Verify that paths for volumes and devices are correct.
- Ensure the network settings, ports, and volume mappings match your specific setup requirements.
- This guide assumes a single instance of **open-webui**. Adjust as needed for multiple containers or different configurations.
