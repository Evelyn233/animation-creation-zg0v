# coding=utf-8
from http import HTTPStatus
import dashscope
import requests
from models import *


def ms_to_srt_timestamp(ms):
    """将毫秒转换为SRT时间戳格式"""
    seconds, milliseconds = divmod(int(ms), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"


def remove_punctuation(text):
    """移除文本中的标点符号"""
    return re.sub(r'[^\w\s]', '', text)


def generate_srt(sentences):
    """生成字幕"""
    srt_content = []
    entry_id = 1

    for sentence in sentences:
        text = sentence['text'].strip()
        words = sentence.get('words', [])
        if not text or not words:
            print(f"Skipping empty sentence with ID {sentence['sentence_id']}.")
            continue

        current_part = ''
        part_start_time = words[0]['begin_time']
        part_end_time = None

        for i, word in enumerate(words):
            current_part += word['text']
            if word['punctuation']:
                part_end_time = word['end_time']
                cleaned_text = remove_punctuation(current_part).strip()
                if cleaned_text:
                    srt_content.append(f"{entry_id}")
                    srt_content.append(
                        f"{ms_to_srt_timestamp(part_start_time)} --> {ms_to_srt_timestamp(part_end_time)}")
                    srt_content.append(cleaned_text)
                    srt_content.append("")
                    entry_id += 1
                current_part = ''
                part_start_time = words[i + 1]['begin_time'] if i + 1 < len(words) else sentence['end_time']
        # 处理最后一部分（如果有的话）
        if current_part.strip():
            part_end_time = words[-1]['end_time']
            cleaned_text = remove_punctuation(current_part).strip()
            if cleaned_text:
                srt_content.append(f"{entry_id}")
                srt_content.append(
                    f"{ms_to_srt_timestamp(part_start_time)} --> {ms_to_srt_timestamp(part_end_time)}")
                srt_content.append(cleaned_text)
                srt_content.append("")
                entry_id += 1
    # 添加一个空的结尾段以确保最后一个段落能显示
    last_entry_lines = srt_content[-4:]
    last_entry_time_end = last_entry_lines[1].split(' --> ')[1]
    srt_content.append(f"{entry_id}")
    srt_content.append(f"{last_entry_time_end} --> {last_entry_time_end}")
    srt_content.append("")
    srt_content.append("")

    return "\n".join(srt_content)


def voice_to_srt(voice_oss_url, srt_source, prompt_id):
    map_index = {}
    file_urls = []
    for key in voice_oss_url:
        map_index[voice_oss_url[key]] = key
        file_urls.append(voice_oss_url[key])
    # 如您未将API Key配置到环境变量中，可带上下面这行代码并将your-dashscope-api-key替换成您自己的API Key
    dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")
    task_response = dashscope.audio.asr.Transcription.async_call(
        model='paraformer-v1',
        file_urls=file_urls,
    )

    transcribe_response = dashscope.audio.asr.Transcription.wait(task=task_response.output.task_id)
    if transcribe_response.status_code == HTTPStatus.OK:
        data = transcribe_response.output
        if data['task_status'] == 'SUCCEEDED':
            result = transcribe_response.output['results']
            for item in result:
                # 对transcription_url发起GET请求
                transcription_response = requests.get(item['transcription_url'])
                # 检查请求是否成功
                if transcription_response.status_code == 200:
                    # 假设返回的内容是文本格式
                    transcription_content = transcription_response.text
                    transcription = json.loads(transcription_content)
                    file_url = transcription['file_url']
                    index = map_index[file_url]
                    transcripts = transcription["transcripts"][0]
                    srt_output = generate_srt(transcripts["sentences"])
                    srt_output = fix_srt(srt_source[index], srt_output)
                    with open(f'factory/{prompt_id}/subtitles/{index}.srt', 'w', encoding='utf-8') as file:
                        file.write(srt_output)
                else:
                    print(f"Failed to retrieve transcription: {transcription_response.status_code}")
            print('transcription done!')
            return True
        else:
            return False
