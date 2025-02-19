# -*- coding: utf-8 -*-
import json
import os
import random
from oss_utils import upload
import requests
import base64
import asyncio

comfyui_base_url = os.environ['COMFYUI_BASE_URL']


def generate_random_seed():
    return random.randint(1, 999999999999999)


def set_scenes(json_data):
    # 原始文本模板
    text_template = '''"0": "{scene0}",\n"1": "{scene1}",\n"2": "{scene2}",\n"3": "{scene3}",\n"4": "{scene4}"'''
    # 创建一个新的字典来保存替换后的文本内容
    new_text_dict = {}

    # 遍历scenes数组，并使用scene_number作为键
    for scene in json_data['chapters']:
        # 因为我们想用0, 1, 2...来对应"0", "1", "2"...我们减去1来得到正确的索引
        index = str(scene['chapter'] - 1)
        new_text_dict[f'scene{index}'] = scene['scene_description_en']

    return text_template.format(**new_text_dict)


async def run_task(scene_description, traits_string, task_id):
    scene_description_string = set_scenes(scene_description)
    url = f"{comfyui_base_url}/api/run"
    payload = json.dumps({
    "10": {
      "inputs": {
        "vae_name": "ae.safetensors"
      },
      "class_type": "VAELoader"
    },
    "11": {
      "inputs": {
        "clip_name1": "t5xxl_fp8_e4m3fn.safetensors",
        "clip_name2": "clip_l.safetensors",
        "type": "flux"
      },
      "class_type": "DualCLIPLoader"
    },
    "12": {
      "inputs": {
        "unet_name": "flux1-schnell-fp8-e4m3fn.safetensors",
        "weight_dtype": "fp8_e4m3fn"
      },
      "class_type": "UNETLoader"
    },
    "13": {
      "inputs": {
        "noise": [
          "25",
          0
        ],
        "guider": [
          "22",
          0
        ],
        "sampler": [
          "16",
          0
        ],
        "sigmas": [
          "17",
          0
        ],
        "latent_image": [
          "66",
          0
        ]
      },
      "class_type": "SamplerCustomAdvanced"
    },
    "16": {
      "inputs": {
        "sampler_name": "euler"
      },
      "class_type": "KSamplerSelect"
    },
    "17": {
      "inputs": {
        "scheduler": "simple",
        "steps": 8,
        "denoise": 1,
        "model": [
          "12",
          0
        ]
      },
      "class_type": "BasicScheduler"
    },
    "22": {
      "inputs": {
        "model": [
          "12",
          0
        ],
        "conditioning": [
          "231",
          0
        ]
      },
      "class_type": "BasicGuider"
    },
    "25": {
      "inputs": {
        "noise_seed": generate_random_seed()
      },
      "class_type": "RandomNoise"
    },
    "64": {
      "inputs": {
        "samples": [
          "13",
          0
        ],
        "vae": [
          "10",
          0
        ]
      },
      "class_type": "VAEDecode"
    },
    "65": {
        "inputs": {
            "filename_prefix": "ComfyUI",
            "images": [
                "64",
                0
            ]
        },
        "class_type": "SaveImage",
        "_meta": {
            "title": "SaveImage"
        }
    },
    "66": {
      "inputs": {
        "width": 1024,
        "height": 1024,
        "batch_size": 1
      },
      "class_type": "EmptyLatentImage"
    },
    "229": {
      "inputs": {
        "prepend_text": "anime style,high quality,"+traits_string,
        "multiline_text": scene_description_string,
        "append_text": "",
        "start_index": 0,
        "max_rows": 1000
      },
      "class_type": "CR Prompt List"
    },
    "231": {
      "inputs": {
        "text": [
          "229",
          0
        ],
        "clip": [
          "11",
          0
        ]
      },
      "class_type": "CLIPTextEncode"
    }
  })

    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/131.0.0.0 Safari/537.36'
    }
    response = await asyncio.to_thread(requests.request, "POST", url, headers=headers, data=payload)
    data = response.json()
    results = data['65']['results']
    oss_urls = await asyncio.to_thread(process_results, results, task_id)
    return oss_urls


def fix_padding_and_decode(base64_string):
    padding = len(base64_string) % 4
    if padding:
        base64_string += '=' * (4 - padding)

    try:
        # 解码Base64字符串为二进制数据
        return base64.b64decode(base64_string)
    except base64.binascii.Error as e:
        return None


def base64_to_png(base64_string, output_filename):
    image_data = fix_padding_and_decode(base64_string)
    if image_data is not None:
        # 将解码后的数据写入PNG文件
        with open(output_filename, 'wb') as file:
            file.write(image_data)
    else:
        print("Failed to decode the Base64 string.")


def process_results(results, prompt_id):
    """处理results数组，将Base64图片数据保存本地并上传OSS"""
    base_image_dir = f"factory/{prompt_id}/images"
    oss_urls = {}
    for i in range(len(results)):
        local_filename = f"{base_image_dir}/{i}.png"
        base64_to_png(results[i], local_filename)
        object_name = f"{prompt_id}/images/{i}.png"
        oss_sign_url = upload(object_name, local_filename)
        oss_urls[str(i)] = oss_sign_url
    return oss_urls
