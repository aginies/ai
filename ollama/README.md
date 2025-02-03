# Ollama Systemd Service Setup

This guide provides a step-by-step process for setting up an **ollama** container as a systemd service. This approach is useful when you want your container to start automatically at boot and be managed through systemd commands.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Steps to Create a Systemd Service](#steps-to-create-a-systemd-service)
  - [1. Define the Systemd Unit File](#1-define-the-systemd-unit-file)
  - [2. Create the Docker Volume](#2-create-the-docker-volume)
  - [3. Reload and Enable the Systemd Service](#3-reload-and-enable-the-systemd-service)
  - [4. Start the Service](#4-start-the-service)
  - [5. Verify the Status](#5-verify-the-status)
- [Managing the Service](#managing-the-service)
- [Notes](#notes)

## Prerequisites

Before starting, ensure you have:

- **Docker** installed and running on your system.
- Sufficient privileges (sudo or root) to create systemd service files and manage Docker volumes.
- Ensure Docker is enabled and managed by systemd.

## Steps to Create a Systemd Service

### 1. Define the Systemd Unit File

Create a new file named `ollama-rocm.service` in `/etc/systemd/system/`. Adjsut the value to your needs, especially the volume. for NVIDIA user set **IMAGES=ollama/ollama**.

```bash
# vi /etc/systemd/system/ollama-rocm.service
[Unit]
Description=Ollama Rocm Container Service
After=docker.service,network-online.target
Requires=docker.service

[Service]
Restart=always
# Mounts a host directory to the container for model storage.
Environment=MODELS=/mnt/data/models:/root/.ollama/models
# Creates and uses a Docker volume for persistent data.
Environment=DATADIR=ollama:/root/.ollama
Environment=PORTS=11434:11434
Environment=IMAGES=ollama/ollama:rocm
ExecStartPre=-/usr/bin/docker rm -f ollama
ExecStart=/usr/bin/docker run --name ollama \
    -v ${MODELS} \
    -v ${DATADIR} \
    --device /dev/kfd:/dev/kfd \ # Grants access to GPU devices required by Ollama.
    --device /dev/dri:/dev/dri \ # Provides direct rendering interfaces from the host.
    -p ${PORTS} \
	${IMAGES}
ExecStop=/usr/bin/docker stop ollama
```

### 2. Create the Docker Volume 

Create a volume named ollama before starting the service: 
```bash
# docker volume create ollama
```
 
### 3. Reload and Enable the Systemd Service 

Inform systemd about the new service and enable it to start at boot: 
```bash
# sudo systemctl daemon-reload
# sudo systemctl enable ollama.service
```
 
### 4. Start the Service 

Begin the ollama service using the following command: 
```bash
# sudo systemctl start ollama.service
```
 
### 5. Verify the Status 

Confirm that the service is running correctly: 
```bash
# sudo systemctl status ollama.service
```

## Managing the Service

- Start : sudo systemctl start ollama.service
- Stop : sudo systemctl stop ollama.service
- Restart : sudo systemctl restart ollama.service
- Status : sudo systemctl status ollama.service
     

## Notes 

- Verify that paths for volumes and devices are correct.
- Ensure the network settings, ports, and volume mappings match your specific setup requirements.
- This guide assumes a single instance of Ollama. Adjust as needed for multiple containers or different configurations.
