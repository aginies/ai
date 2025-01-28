# Goal

Easily deploy containers to create AI images for **AMD GPU** or **NVIDIA GPU**.

| Project | Container size | OS | Advantages | Drawbacks | 
| :--------------- | :---: | :---: |:---: | :---: |
| [ComfyUI](https://www.comfy.org/) | 26Gb  | Leap15.6 | Huge customisation possible, no limit | Could be complex as there is a lot of custom_nodes available |
| [LocalAI web](https://github.com/mudler/LocalAI) | 109Gb | Ubuntu | Easy to deploy and include other AI stuff |  Limited for the image part |
| [AUTOMATIC1111](https://github.com/AUTOMATIC1111/stable-diffusion-webui) | 23.9Gb | Leap15.6 | Lot of capabilities | Limited and UI layout is confusing |

I recommend to use [ComfyUI](https://www.comfy.org/) as the interface is really powerfull and there is tons of capabilies.

# AMD GPU card and Tweaking

You need to install [AMD GPU](https://rocm.docs.amd.com/projects/install-on-linux/en/latest/install/amdgpu-install.html#suse-linux-enterprise) to get the kernel module from AMD, this will **dkms** rebuild the module.

At home I have a Radeon Merc310 7900XT, I tweak it a bit to improve the performance. There is some really good information at [AMD GPU](https://wiki.archlinux.org/title/AMDGPU). Create a **/etc/systemd/system/set-gpu-settings.service** with your values to get this applied to your system permanently.

**⚠️ Warning:** Use this options with care, as this can lead to unstable system or domage your hardware!

| Parameter | Value | Real |
| :--------------- | :---: | :---: |
| Max Power | 300000000 | 300W |
| Memory Clock | 1350 | 1350MHz |
| GPU Clock | 2900 | 2900MHz |

```systemd
[Unit]
Description=Set GPU power cap and clock
After=multi-user.target

[Service]
Type=oneshot
ExecStart=/bin/bash -c "echo 300000000 > /sys/class/drm/card0/device/hwmon/hwmon1/power1_cap"
ExecStart=/bin/bash -c "echo 'm 1 1350' > /sys/class/drm/card0/device/pp_od_clk_voltage"
ExecStart=/bin/bash -c "echo 's 1 2900' | sudo tee /sys/class/drm/card0/device/pp_od_clk_voltage"
ExecStart=/bin/bash -c "echo c > /sys/class/drm/card0/device/pp_od_clk_voltage"
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
```

Enable it now and at boot:
```bash
sudo systemctl daemon-reload
sudo systemctl enable set-power-cap.service --now
sudo systemctl start set-power-cap.service
sudo systemctl status set-power-cap.service
```

# NVIDIA GPU

Install the [Nvidia GPU driver](https://en.opensuse.org/SDB:NVIDIA_drivers). Check everything is ok after a reboot with the **nvidia-smi** command.
Prepare docker, you need to install [container-toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html#installing-with-zypper)

# ComfyUI container

ComfyUI service will be available at [http://YOURIP:8188](http://YOURIP:8188) as the option **--listen is enable**.
**models**, **custom nodes**, **created images** and **workflow** should be stored
outside of the containers. So check the volume in **docker-compose.yaml** file.

By default this container will be prepared for some **custom_nodes** requirements, but you need to clone it into your home directory to get them available. Check the **volume**
directory in the **docker-compose.yaml** file.

- [ComfyUI-Manager](https://github.com/ltdrdata/ComfyUI-Manager)
- [ComfyUI_ExtraModels](https://github.com/city96/ComfyUI_ExtraModels)
- [comfyui-controlnet-aux](https://github.com/comfyorg/comfyui-controlnet-aux)
- [ComfyUI-WD14-Tagger](https://github.com/pythongosssss/ComfyUI-WD14-Tagger)
- [stability-ComfyUI-nodes](https://github.com/Stability-AI/stability-ComfyUI-nodes)


## ComfyUI_AMD/docker-compose.yaml

Create the container ComfyUI for **AMDGPU / rocm**.
It will use Rocm 6.3 development release. You can use a stable one like 6.2, change the **pip install** in the **Dockerfile** to something like:

```dockerfile
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/rocm6.2
```

## ComfyUI_NVIDIA/docker-compose.yaml

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


# localai/docker-compose.yaml

Create the container localAI for AMDGPU with rocm.
LocalAI service will be available at [http://YOURIP:8080](http://YOURIP:8080)

## HowTo LocalAI

Adjust the **docker-compose.yaml**

```bash
cd localai
docker compose build
docker compose up
```

## Improved  Web page to generate Images

### web/imageai.html

Page to easily configure the creation of an AI Image.
Open the script an adapt the url to you localAI server.

```bash
grep -n "const serverUrl" imageai.html 
398:   const serverUrl = 'http://10.0.1.38:8080';
```

![image](https://github.com/aginies/ai/blob/baf95ed9f6d0a1d9df64e20a64712e217ab23bdd/images/imageai.jpg)

# stable-diffusion-webui/docker-compose.yaml

This container is using a openSUSE Leap15.6 OS and prepare everythign to get stable-diffusion-webui for AMDGPU. Service will be available at: [http://YOURIP:7860](http://YOURIP:7860)

## HowTo stable-diffusion-webui

Preparing the container can take a while, be patient as there is Gb of downloads.

```bash
cd stable-diffusion-webui
docker compose build
docker compose up
```

### Help Debug

Rebuild with no previous build:
```bash
docker-compose down --rmi local -v
docker-compose build --no-cache
```

Debug the stable-diffusion-webui container:
```
docker run -e LISTEN="" -e BUILD=debug -it stable-diffusion-webui:latest
```

# web/serverhttp.py

Quick python http server to get the **imageai.html** available on a web page.
Create a directory, put the file in, launch the **serverhttp.py** script as a user.
Default port is **8081**.

```bash
mkdir ai
cp imageai.html ai/
cd ai
python3.11 serverhttp.py
```

# server_gallery_images.py

Quick python http server to show all the images by date creation on a web page (port 8000). It supports a modal display mode to quickly view all the images.

## ComfyUI

Adjust the **IMAGES_DIR** var to your path:
```
IMAGES_DIR = "/home/aginies/comfyUI/output"
```

```bash
cp server_gallery_images.py /home/aginies/comfyUI/
cd /home/aginies/comfyUI
python3.11 server_gallery_images.py
```

![image](https://github.com/aginies/ai/blob/5e534bbece9069158b9d093a95ba16f3c0af35f1/images/serverimage.jpg)


## systemd service

**/etc/systemd/system/serverimage.service**:
```systemd
[Unit]
Description=Images Gallery
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3.11 /home/aginies/comfyUI/server_gallery_images.py
WorkingDirectory=/home/aginies/comfyUI
User=root
Group=root
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable it now and at boot:
```bash
sudo systemctl daemon-reload
sudo systemctl enable serverimage.service --now
sudo systemctl start serverimage.service
sudo systemctl status serverimage.service
```


# External URL

LocalAI and rocm:
- [localAI](https://localai.io/)
- [rocm AMD Doc](https://rocm.docs.amd.com/en/docs-6.2.4/index.html)

stable-diffusion-webui:
- [AUTOMATIC1111](https://github.com/AUTOMATIC1111/stable-diffusion-webui)
- [stable-diffusion-webui-amdgpu](https://github.com/lshqqytiger/stable-diffusion-webui-amdgpu.git)

Models:
- [huggingface.co](https://huggingface.co/models?pipeline_tag=text-to-image&sort=trending)
- [civitai.co](https://civitai.com/models)

External Doc:
- [SUSE Generating Images](https://www.suse.com/c/generating-images-with-localai-using-a-gpu/)
