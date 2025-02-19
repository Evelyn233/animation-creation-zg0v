# -*- coding: utf-8 -*-

import os

from moviepy import *
from moviepy.video.VideoClip import TextClip
from moviepy.video.compositing.CompositeVideoClip import (
    CompositeVideoClip
)
from moviepy.video.tools.subtitles import SubtitlesClip

from animation import random_scroll_animation


def add_subtitles_to_video(video_path, subtitles_path, output_path,
                           font="font/Alibaba-PuHuiTi-Bold.otf",
                           font_size=28, text_color="yellow", margin_bottom=300):
    """
    给指定的视频添加字幕并保存为新文件。

    :param video_path: 视频文件路径
    :param subtitles_path: 字幕文件路径（.srt格式）
    :param output_path: 输出带字幕的视频文件路径
    :param font: 字体名称，默认为'SourceHanSansSC-Normal-Min.ttf'
    :param font_size: 字体大小，默认为24
    :param text_color: 文本颜色，默认为'white'
    :param margin_bottom: 字幕与视频底部的间距，默认为40像素
    """
    video = VideoFileClip(video_path)
    generator = lambda txt: TextClip(
        text=txt,
        font=font,
        size=(800, 600),
        font_size=font_size,
        method="caption",
        vertical_align="bottom",
        color=text_color,
    )
    subs = SubtitlesClip(subtitles_path, make_textclip=generator)
    if subs.duration is None or subs.duration > video.duration:
        subs = subs.with_duration(video.duration)

    max_subs_height = font_size
    subs_y_position_relative = ('center', (margin_bottom + max_subs_height) / video.size[1])
    subs = subs.with_position(subs_y_position_relative, relative=True)
    video_with_subs = CompositeVideoClip([video, subs])
    video_with_subs.write_videofile(output_path, codec="libx264", audio_codec="aac", threads=2, logger=None)


def create_video(prompt_id, image_dir_path="images", audio_dir_path="audios", subtitle_dir_path="subtitles",
                 output_dir="out"):
    image_dir_path = f"factory/{prompt_id}/{image_dir_path}"
    audio_dir_path = f"factory/{prompt_id}/{audio_dir_path}"
    subtitle_dir_path = f"factory/{prompt_id}/{subtitle_dir_path}"
    output_dir = f"factory/{prompt_id}/{output_dir}"

    audio_files = os.listdir(audio_dir_path)
    for i in range(len(audio_files)):
        image_path = os.path.join(image_dir_path, str(i) + ".png")
        audio_path = os.path.join(audio_dir_path, str(i) + ".mp3")
        temp_path = f'{image_dir_path}/{str(i)}.mp4'
        selected_animation = random_scroll_animation()
        selected_animation(image_path=image_path, audio_path=audio_path, output_path=temp_path)
        subtitle_path = os.path.join(subtitle_dir_path, str(i) + ".srt")
        out_subtitles_path = f"{output_dir}/{str(i)}.mp4"
        add_subtitles_to_video(temp_path, subtitle_path, out_subtitles_path)
    output_file = f"{output_dir}/out.mp4"
    # 获取按序号排序的视频文件列表
    video_files = get_sorted_video_files(output_dir)
    if not video_files:
        print("没有找到可处理的视频文件。")
    else:
        # 执行合并操作
        merge_videos(video_files, output_file)
        print(f"视频已成功合并并保存为 {output_file}")
    return output_file


def get_sorted_video_files(directory):
    """从指定目录中获取并按文件序号排序的视频文件列表"""
    # 获取目录中所有 .mp4 文件
    video_files = [f for f in os.listdir(directory) if f.endswith('.mp4')]
    try:
        video_files.sort(key=lambda x: int(os.path.splitext(x)[0]))
    except ValueError:
        return []
    video_files = [os.path.join(directory, f) for f in video_files]
    return video_files


def merge_videos(video_files, output_file):
    """合并多个视频文件为一个视频文件"""
    # 读取所有视频文件
    clips = [VideoFileClip(video) for video in video_files]
    # 拼接视频
    final_clip = concatenate_videoclips(clips, method="compose")
    # 导出合并后的视频
    final_clip.write_videofile(output_file, threads=2, logger=None, codec='libx264', audio_codec='aac')

