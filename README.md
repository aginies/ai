# Goal

Easily deploy localAI at home and use it to generate images.

# docker-compose.yaml

Create the container for AMDGPU with rocm and localAI.

# imageai.html

Page to easily configure the creation of an AI Image.
Open the script an adapt the url to you localAI server.

```bash
grep "const serverUrl" imageai.html 
398:   const serverUrl = 'http://10.0.1.38:8080';
```

![image](https://github.com/aginies/ai/blob/774865c449736b9cef8f41f49cb5a3734fc5d060/images/imageai.jpg)

# serverhttp.py

Quick python http server to get the **imageai.html** available on a server.
Create a directory, put the file in, launch the **serverhttp.py** script as a user.
Default port is **8081**.

```bash
mkdir ai
cp imageai.html ai
python3.11 serverhttp.py
```

# External URL

LocalAI and rocm:
- https://localai.io/
- https://rocm.docs.amd.com/en/docs-6.2.4/index.html

Models:
- https://huggingface.co/models?pipeline_tag=text-to-image&sort=trending
- https://civitai.com/models

External Doc:
- https://www.suse.com/c/generating-images-with-localai-using-a-gpu/
