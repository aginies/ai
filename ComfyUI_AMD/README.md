# ComfyUI container

ComfyUI service will be available at [http://YOURIP:8188](http://YOURIP:8188) as the option **--listen** is enable.
[models](#models), **custom nodes**, **created images** and **workflow** should be stored
outside of the containers. So check the volume in **docker-compose.yaml** [config](## HowTo-configure-ComfyUI).

By default this container will be prepared for some **custom_nodes** requirements, but you need to clone it into your home directory to get them available. Check the **volume**
directory in the **docker-compose.yaml** file.

- [ComfyUI-Manager](https://github.com/ltdrdata/ComfyUI-Manager)
- [ComfyUI_ExtraModels](https://github.com/city96/ComfyUI_ExtraModels)
- [comfyui-controlnet-aux](https://github.com/comfyorg/comfyui-controlnet-aux)
- [ComfyUI-WD14-Tagger](https://github.com/pythongosssss/ComfyUI-WD14-Tagger)
- [stability-ComfyUI-nodes](https://github.com/Stability-AI/stability-ComfyUI-nodes)


## AMD/docker-compose.yaml

Create the container ComfyUI for **AMDGPU / rocm**.
It will use Rocm 6.3 development release. You can use a stable one like 6.2, change the line which contains **rocm6.3** in the **Dockerfile** to something like:

```dockerfile
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/rocm6.2
```

Also you need to adjust the **GFX** var in the **docker-compose.yaml** to your [card](https://rocm.docs.amd.com/projects/install-on-linux/en/latest/reference/system-requirements.html)

## NVIDIA/docker-compose.yaml

Create the container ComfyUI for **NVIDIA / cuda**.

## HowTo configure ComfyUI

Adjust the volume in **docker-compose.yaml**:
```docker
    volumes:
      # models
      - /mnt/data/models:/ComfyUI/models
      # create images
      - /home/aginies/comfyUI/output:/ComfyUI/output
      # workflow path
      - /home/aginies/comfyUI/my_workflows:/ComfyUI/my_workflows
      # custom nodes
      - /home/aginies/comfyUI/custom_nodes:/ComfyUI/custom_nodes
      # settings
      - /home/aginies/comfy.settings.json:/ComfyUI/user/default/comfy.settings.json
```

```bash
docker compose build
docker compose up
```

## Test some ComfyUI start options

Modify the **docker-compose.yaml** file and set **BUILD** value to **debug**. Start the container:

```bash
docker compose up
[+] Building 0.0s (0/0)                                                                   docker:default
[+] Running 1/0
 ✔ Container comfyui  Created                                                                       0.0s
Attaching to comfyui
comfyui  | To Debug it:
comfyui  | docker exec -it comfyui /bin/bash
```

Go inside the container and test some parameters:
```
docker exec -it comfyui /bin/bash
export PYBIN=python3.11
export SDW_DIR=/ComfyUI
export DIR_TO_CHECK=${SDW_DIR}/venv
source ${DIR_TO_CHECK}/bin/activate
cd ${SDW_DIR}
python3.11 main.py --help
usage: main.py [-h] [--listen [IP]] [--port PORT] [--tls-keyfile TLS_KEYFILE]
               [--tls-certfile TLS_CERTFILE] [--enable-cors-header [ORIGIN]]
               [--max-upload-size MAX_UPLOAD_SIZE] [--extra-model-paths-config PATH [PATH ...]]
               [--output-directory OUTPUT_DIRECTORY] [--temp-directory TEMP_DIRECTORY]
               [--input-directory INPUT_DIRECTORY] [--auto-launch] [--disable-auto-launch]
               [--cuda-device DEVICE_ID] [--cuda-malloc | --disable-cuda-malloc]
               [--force-fp32 | --force-fp16]
               [--fp32-unet | --fp64-unet | --bf16-unet | --fp16-unet | --fp8_e4m3fn-unet | --fp8_e5m2-unet]
               [--fp16-vae | --fp32-vae | --bf16-vae] [--cpu-vae]
               [--fp8_e4m3fn-text-enc | --fp8_e5m2-text-enc | --fp16-text-enc | --fp32-text-enc]
               [--force-channels-last] [--directml [DIRECTML_DEVICE]]
               [--oneapi-device-selector SELECTOR_STRING] [--disable-ipex-optimize]
               [--preview-method [none,auto,latent2rgb,taesd]] [--preview-size PREVIEW_SIZE]
               [--cache-classic | --cache-lru CACHE_LRU]
               [--use-split-cross-attention | --use-quad-cross-attention | --use-pytorch-cross-attention | --use-sage-attention]
               [--disable-xformers] [--force-upcast-attention | --dont-upcast-attention]
               [--gpu-only | --highvram | --normalvram | --lowvram | --novram | --cpu]
               [--reserve-vram RESERVE_VRAM] [--default-hashing-function {md5,sha1,sha256,sha512}]
               [--disable-smart-memory] [--deterministic] [--fast] [--dont-print-server]
               [--quick-test-for-ci] [--windows-standalone-build] [--disable-metadata]
               [--disable-all-custom-nodes] [--multi-user]

               [--verbose [{DEBUG,INFO,WARNING,ERROR,CRITICAL}]] [--log-stdout]
               [--front-end-version FRONT_END_VERSION] [--front-end-root FRONT_END_ROOT]
               [--user-directory USER_DIRECTORY]

HSA_OVERRIDE_GFX_VERSION=11.0.0 PYTORCH_HIP_ALLOC_CONF=expandable_segments:True TORCH_ROCM_AOTRITON_ENABLE_EXPERIMENTAL=1 ${PYBIN} main.py --force-fp16 --preview-method auto --gpu-only
```

## HowTo add custom_nodes with some python requirements

A lot of **custome_nodes** are available, some needs some python requirements. You need to update the **pip install** command at the end of the **ComfyUI_XYX/Dockerfile** file to get them ready in the container.

```
RUN cd ComfyUI \
    && python3.11 -m venv venv \
    && source venv/bin/activate \
    && pip install --upgrade pip wheel \
    && pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm6.2
\
    && pip install -r requirements.txt \
    && pip install -r https://github.com/comfyanonymous/ComfyUI/raw/refs/heads/master/requirements.txt \
         -r https://github.com/ltdrdata/ComfyUI-Manager/raw/refs/heads/main/requirements.txt -r YOURREQUIREMENTSFILE
```

PS: You need to rebuild your container after this modification.

# ComfyUI Service Setup for AMD GPUs

This guide provides instructions on setting up a systemd service to manage a Docker container running ComfyUI, optimized for AMD GPU systems.

## Prerequisites

- **Docker**: Ensure Docker is installed and the `docker.service` is active.
- **AMD GPU**: A system with an AMD GPU that supports ROCm or similar frameworks.
- **Systemd**: Your Linux distribution should support systemd for service management.

# Systemd Service Configuration

Create a systemd service file, e.g., `/etc/systemd/system/comfyui.service`, with the following content:

```ini
[Unit]
Description=ComfyUI for AMD
After=docker.service,network-online.target
Requires=docker.service

[Service]
Restart=always
RestartSec=30
TimeoutStopSec=70
Environment=GFX=11.0.0
Environment=BUILD=false
Environment=GPU=AMD
Environment=OPTIONS=--listen --use-pytorch-cross-attention

ExecStartPre=-/usr/bin/docker rm -f comfyui-amd
ExecStart=/usr/bin/docker run --name comfyui-amd \
    --privileged \
    --network host \
    -e BUILD=${BUILD} \
    -e GFX=${GFX} \
    -e GPU=${GPU} \
    -e OPTIONS="--listen --use-pytorch-cross-attention" \
    -v /mnt/data/models:/ComfyUI/models \
    -v /home/aginies/comfyUI/output:/ComfyUI/output \
    -v /home/aginies/comfyUI/my_workflows:/ComfyUI/my_workflows \
    -v /home/aginies/comfyUI/custom_nodes:/ComfyUI/custom_nodes \
    -v /home/aginies/comfyUI/comfy.settings.json:/ComfyUI/user/default/comfy.settings.json \
    --device /dev/dri \
    --device /dev/kfd \
comfyui-amd

ExecStop=/usr/bin/docker stop comfyui-amd

[Install]
WantedBy=multi-user.target default.target


## Instructions to Enable and Start the Service 

Create the Service File, saving the above configuration in `/etc/systemd/system/comfyui.service`

Reload Systemd Daemon:
```bash
# sudo systemctl daemon-reload
```

Enable the service:
```bash
sudo systemctl enable comfyui
```
 
Start the Service:
```bash
sudo systemctl start comfyui
```
 
Verify the Service Status:
```bash
sudo systemctl status comfyui
```
     
## Volume Mounting 

Ensure that your directory paths for volumes (`/mnt/data/models`, `/home/aginies/comfyUI/output`, etc.) exist and have appropriate permissions. 

## Customization 

Adjust Environment variables as needed, particularly if different versions of ROCm or other configurations are required. Modify volume paths to match the user's file system layout.
     
This setup ensures that ComfyUI runs efficiently on AMD or Nvidia hardware with automatic restarts and proper resource allocation. For troubleshooting, refer to systemd logs using **journalctl -fu comfyui**.
