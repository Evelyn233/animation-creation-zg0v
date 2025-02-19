# -*- coding: utf-8 -*-
import json
import os
import re

from openai import OpenAI

client = OpenAI(
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)


def extract_features(image_url):
    """提取任务特征描述"""
    completion = client.chat.completions.create(
        model='qwen-vl-max',  # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
        messages=[
            {'role': 'system', 'content': '你是人物特征信息提取专家，擅长提取，人物五官信息。'},
            {
                'role': 'user',
                'content': [
                    {
                        'type': 'image_url',
                        'image_url': {
                            'url': image_url
                        }
                    },
                    {
                        'type': 'text',
                        'text': "请按照以下输出格式示例提取主体人物信息  # 输出格式示例：性别（男/女），年龄（0-6/7-13/14-19/20-24/25-30/30-45/46-60/61-80），眼睛（单眼皮/双眼皮，黑色/棕色/蓝色/绿色/灰色瞳孔），头发（长/短/，黑色/黄色）"
                    },
                    {

                        'type': 'text',
                        'text': "严格按照输出格式示例输出结果，不要输出任何额外信息。"
                    }
                ]
            }
        ])

    return completion.choices[0].message.content


def make_chapters(subject, traits_prompt):
    """生成小说章节"""
    prompt = (
        "# 角色\n"
        "你是一名专业小说家和人物形象描绘译专家，擅长撰写各种沙雕小说和人物形象描绘。\n\n"
        "# 任务描述\n"
        "## 一、给你一段小说简介，请你完成以下任务。\n"
        "- 请根据小说简介写一篇精彩的小说。\n"
        "- 请给小说起一个通熟易懂，看一眼就停不下来的，吸引人的名字，需要突出小说的内容，要求6-10个汉字。\n"
        "- 小说采用 JSON 输出。\n"
        "- 编写300字小说。\n"
        "- 小说分为5个章节。\n"
        "- 小说章节内容要丰富精彩 content 字数大于 45 个汉字或英文文字。\n"
        "- 5个章节 content 总长要大于300个汉字或英文文字。\n"
        "- 场景描述 scene_description ，需要丰富精彩，增加下人物比例的描述，人物不能占满整个场景。\n"
        "- 只使用逗号和句号来断句。\n"
        "## 二、根据人物简单描述信息，小说简介，完成主角形象描述。。\n"
        "### 参考模版\n"
        "- 人物形象描述：一位三十岁左右的亚洲女性，面容精致且极具东方韵味，眼眸深邃而明亮，透着坚韧与智慧，高挺的鼻梁下是微微上扬的嘴角，展现出自信又亲和的气质。身形高挑且苗条，身姿挺拔，举手投足间尽显优雅干练。\n"
        "- 人物形象提示词：30-year-old Asian woman, delicate and oriental facial features, deep and bright eyes showing "
        "tenacity"
        "and wisdom, a slightly upturned mouth under the high nose bridge, confident and approachable temperament, "
        "tall and slender figure, elegant and capable in every move.\n\n"
        "- 结果与任务一统一放在一个 JSON 中，字段 traits_prompt 和 traits_prompt_en 。\n"
        "# 输入数据\n"
        "## 人物简单描述信息\n"
        f"{traits_prompt}\n"
        "## 小说简介\n"
        f"{subject}\n"
        "# 输出格式\n"
        "{\"name\": \"小说名字\"，\"chapters\": [{\"chapter\": 0, \"title\": \"章节标题\",\"content\": \"小说内容\","
        "\"scene_description\": \"场景描述\","
        "\"scene_description_en\": \"场景英文描述\"}],\"traits_prompt\": \"人物形象描述\",\"traits_prompt_en\": \"人物形象提示词\"}\n\n"
        "# 限制\n"
        "- content 小说章节内容长度要丰富，内容必须大于45个汉字或英文文字。\n"
        "- 章节中断句不得超过18个汉字或英文字符，包括标点符号。\n"
    )

    completion = client.chat.completions.create(
        model="qwen-max-latest",  # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
        messages=[
            {'role': 'system', 'content': '你是一名专业小说家和中英文翻译专家，擅长撰写各种沙雕小说和中英文翻译。'},
            {'role': 'user', 'content': prompt},
            {'role': 'user',
             'content': '请确保每个章节的 content 字数大于100个汉字或英文文字，并且总字数超过500个汉字或英文文字。'}
        ],
    )
    data = completion.choices[0].message.content
    try:
        data = json.loads(data)
    except:
        data = json.loads(extract_code_blocks(data))
    return data


def fix_srt(src_text, srt_text):
    """修复字幕错别字"""
    prompt = (
        "# 角色\n"
        "你是一名专业字幕文字校验助手，擅长根据参照文本修复字幕文本中的错别字。\n\n"
        "# 任务描述\n"
        "给你一段参照文本和视频字幕文本请你完成以下任务。\n"
        "- 请根据参照文本复字幕文本中的错别字。\n"
        "# 输入数据\n"
        "## 参照文本\n"
        f"{src_text}\n\n"
        "## 视频字幕文本\n"
        f"{srt_text}\n\n"
        "# 输出格式\n"
        "直接输出内容，不要附带输出任何其他信息和格式。\n"
        "保留完整的SRT字幕文件格式，请仔细检查视频字幕文本是否与原始数据内容一致，注意修改字幕中的错别字，如果没有错别字直接返回输入的视频字幕文本，不要做任何额外的加工。\n")

    completion = client.chat.completions.create(
        model="qwen-max-latest",  # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
        messages=[
            {'role': 'user', 'content': prompt}],
    )
    return completion.choices[0].message.content


def extract_code_blocks(text):
    """ 正则表达式匹配  json包裹的代码块 """
    pattern = r'```json\n(.*?)```'
    code_blocks = re.findall(pattern, text, re.DOTALL)

    if len(code_blocks) > 0:
        return code_blocks[0]

    return ''
