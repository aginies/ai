# Goal

Easily deploy containers to create AI images or use **LLM** for **AMD** or **NVIDIA**.

| Project | Container size | OS | Advantages | Drawbacks | 
| :--------------- | :---: | :---: |:---: | :---: |
| [ComfyUI](https://www.comfy.org/) | 26Gb  | OpenSUSE Leap15.6 | Huge customisation possible, no limit | Could be complex as there is a lot of custom_nodes available |
| [LocalAI web](https://github.com/mudler/LocalAI) | 109Gb | Ubuntu | Easy to deploy and include other AI stuff |  Limited for the image part |
| [AUTOMATIC1111](https://github.com/AUTOMATIC1111/stable-diffusion-webui) | 23.9Gb | OpenSUSE Leap15.6 | Lot of capabilities | Limited and UI layout is confusing |
| [ollama](https://ollama.com/) | 8.3Gb | Ubuntu 22.04.5 LTS | Very powerfull |Need an interface, can't use LM Studio model without conversion |
| [openWebUI](https://docs.openwebui.com/) | 4.3Gb | Debian GNU/Linux 12 | perfect GPT clone | Disabling some stuff is mandatory to avoid overcharged interface |


## Image Generation

I recommend using [ComfyUI](https://www.comfy.org/) to generate images, as its interface is powerful and offers a wide range of capabilities and generate high-quality images.

## Managing Large Language Models (LLM)

For managing **LLMs**, I highly suggest using [ollama](https://ollama.com/). It provides robust tools to handle the complexities associated with large language models effectively.

Additionally, if you're looking for an excellent interface to use your **LLMs**, consider [openWebUI](https://docs.openwebui.com/), which offers a seamless user experience and advanced features.

# GPU Hardware

## Hardware Recommendations

To enhance performance and ensure smooth operation, especially when dealing with resource-intensive tasks such as image generation or handling large language models, I recommend using a VGPU (Virtual GPU) with ample VRAM (Video RAM). A high-performance VGPU will significantly improve the rendering speed and overall efficiency of your workflow.

For optimal performance, consider the following specifications:
- **VRAM:** At least 8 GB of VRAM is recommended. For heavy workloads, 16 GB or more would be ideal.
- **CUDA Cores/Stream Processors:** Ensure your VGPU has a sufficient number of CUDA cores (Nvidia) or Stream Processors (AMD) cores for efficient processing.
- **Bandwidth:** High bandwidth to handle large datasets and complex computations.

### NVIDIA:
- **NVIDIA vGPU:** Offers a comprehensive suite of VGPU solutions, including CUDA cores for parallel computing tasks.
- **NVIDIA Tensor Core GPUs:** Optimized for deep learning and AI workloads.

#### AMD:
- **AMD Radeon Pro:** Provides powerful GPU solutions for professional workflows, with a focus on Stream Processors.
- **ROCM (Radeon Open Compute):** An open-source platform for GPU computing that supports AMD GPUs.

### NVIDIA CUDA Leadership

NVIDIA's CUDA technology is widely recognized as the industry standard for parallel computing. With thousands of developers and organizations leveraging CUDA for various applications, including deep learning, scientific computing, and graphics rendering, it has become a cornerstone in modern high-performance computing environments.


## AMD GPU card and Tweaking

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

## NVIDIA GPU

Install the [Nvidia GPU driver](https://en.opensuse.org/SDB:NVIDIA_drivers). Check everything is ok after a reboot with the **nvidia-smi** command.
Prepare docker, you need to install [container-toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html#installing-with-zypper)

# ComfyUI container

README.md in the ComfyUI_AMD Directory.

# ollama container

README.md in the ollama Directory.

# OpenWebUI container

README.md in the OpenWebUI Directory.

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

# web/server_gallery_images.py

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

## Rocm
- [rocm AMD Doc](https://rocm.docs.amd.com/en/docs-6.2.4/index.html)

## stable-diffusion-webui
- [stable-diffusion-webui-amdgpu](https://github.com/lshqqytiger/stable-diffusion-webui-amdgpu.git)

## models
- [huggingface.co](https://huggingface.co/models?pipeline_tag=text-to-image&sort=trending)
- [civitai.co](https://civitai.com/models)

## SUSE Doc
- [SUSE Generating Images](https://www.suse.com/c/generating-images-with-localai-using-a-gpu/)
