# coding=utf-8
import os

import dashscope
from dashscope.audio.tts_v2 import *
from oss_utils import upload
from srt import voice_to_srt
import asyncio

dashscope.api_key = os.environ['DASHSCOPE_API_KEY']
model = "cosyvoice-v1"


async def create_voice(description, prompt_id, voice):
    voice_oss_url = {}
    tasks = []
    for key in description:
        text = description[key]
        audio = await asyncio.to_thread(lambda t=text: SpeechSynthesizer(model=model, voice=voice).call(t))
        out_path = f'factory/{prompt_id}/audios/{key}.mp3'
        object_name = f"{prompt_id}/audios/{key}.mp3"
        await asyncio.to_thread(lambda p=out_path, a=audio: open(p, 'wb').write(a))
        oss_url = await asyncio.to_thread(upload, object_name, out_path)
        voice_oss_url[key] = oss_url
    await asyncio.to_thread(voice_to_srt, voice_oss_url, description, prompt_id)
    return voice_oss_url
