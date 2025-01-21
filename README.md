# Goal

Easily deploy containers to create AI images for AMD GPU.

- The best one is: [ComfyUI](https://www.comfy.org/)
- [LocalAI web](https://github.com/mudler/LocalAI)
- [AUTOMATIC1111](https://github.com/AUTOMATIC1111/stable-diffusion-webui)
- [stable-diffusion-webui-amdgpu](https://github.com/lshqqytiger/stable-diffusion-webui-amdgpu.git)

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

# Web page to generate Images

config.json  generate_lora_json.py  imageai.html  lora.json  serverhttp.py

## web/imageai.html

Page to easily configure the creation of an AI Image.
Open the script an adapt the url to you localAI server.

```bash
grep -n "const serverUrl" imageai.html 
398:   const serverUrl = 'http://10.0.1.38:8080';
```

**web/config.json** file is used to set all parameters in the web page.

## web/lora stuff

- **web/lora.json** is used to populate the web page.
- **generate_lora_json.py** is a script to generate the **lora.json** file from a directory will all the safetensors files

![image](https://github.com/aginies/ai/blob/774865c449736b9cef8f41f49cb5a3734fc5d060/images/imageai.jpg)


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

Quick server to show all the images by date creation on a page (port 8000). It support a modal display mode to quickly view all the images.

![image](https://github.com/aginies/ai/blob/c153a4708663c8cf66662107e2111da04ff7071e/images/serverimage.jpg)

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
