# Goal

Easily deploy containers to create AI images for AMD GPU.

- The best one is: [ComfyUI](https://www.comfy.org/)
- [LocalAI web](https://github.com/mudler/LocalAI)
- [AUTOMATIC1111](https://github.com/AUTOMATIC1111/stable-diffusion-webui)
- [stable-diffusion-webui-amdgpu](https://github.com/lshqqytiger/stable-diffusion-webui-amdgpu.git)

# Tweak GPU cards

**⚠️ Warning:** Use this options with care, as this can lead to unstable system or domage your hardware!

Got a Radeon Merc310 7900XT, I tweak it to improve the performance. There is some really good information at [AMD GPU](https://wiki.archlinux.org/title/AMDGPU). Create a **/etc/systemd/system/set-gpu-settings.service** with your value to get this applied to your system permanently.

| Parameter | Value | Real |
| :--------------- | :---: | :---: |
| Max Power | 300000000 | 300W |



| Parameter | Value | Real | 
| -------------- | -------------- |
| Max power | 300000000 | 300W |
| Memory Clock | 1350 | 1350 MHz |
| GPU Clock| 2900 | 2900MHz |

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

# ComfyUI/docker-compose.yaml

Create the container localAI for AMDGPU with rocm.
ComfyUI service will be available at [http://YOURIP:8188](http://YOURIP:8188).
**models**, **custom nodes**, **created images** and **workflow** should be stored
outside of the containers. So check the volume in **docker-compose.yaml** file.

## HowTo ComfyUI

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

## HowTo add custom_nodes with some python requirements

A lot of **custome_nodes** are available, some needs some python requirements. You need to update the **pip install** command at the end of the **ComfyUI/Dockerfile** file to get them ready in the container.


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

PS: You need to rebuild your container.

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

![image](https://github.com/aginies/ai/blob/774865c449736b9cef8f41f49cb5a3734fc5d060/images/imageai.jpg)


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

Quick python http server to get the **imageai.html** available on a server.
Create a directory, put the file in, launch the **serverhttp.py** script as a user.
Default port is **8081**.

```bash
mkdir ai
cp imageai.html ai/
python3.11 serverhttp.py
```

# serverimage.py

Quick server to show all the images by date creation on a page (port 8000). It supports a modal display mode to quickly view all the images.

![image](https://github.com/aginies/ai/blob/baf95ed9f6d0a1d9df64e20a64712e217ab23bdd/images/imageai.jpg)

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
