# -*- coding: utf-8 -*-
import random

from moviepy import *
import numpy as np
from PIL import Image


def create_left_to_right_and_center_video(image_path, audio_path, output_path, height=1024, width=768, fps=24):
    image_clip = ImageClip(image_path)
    audio_clip = AudioFileClip(audio_path)
    img_width, img_height = image_clip.size
    assert img_width == 1024 and img_height == 1024, "图像尺寸必须是 1024x1024"
    target_height = height
    target_width = width
    frames = []
    total_frames = int(audio_clip.duration * fps)
    half_frames = total_frames // 2

    def create_frame(offset_x, offset_y, frame):
        new_frame = np.zeros((target_height, target_width, 3), dtype=np.uint8)
        paste_height = min(target_height, img_height - offset_y)
        paste_width = min(target_width, img_width - offset_x)
        paste_x = 0
        paste_y = 0
        new_frame[paste_y:paste_y + paste_height, paste_x:paste_x + paste_width, :] = frame[
                                                                                      offset_y:offset_y + paste_height,
                                                                                      offset_x:offset_x + paste_width,
                                                                                      :]
        return new_frame

    for i in range(half_frames):
        offset_x = int((img_width - target_width) / half_frames * i)
        offset_y = 0
        offset_x = max(0, min(offset_x, img_width - target_width))
        frame = image_clip.get_frame(i / fps)
        new_frame = create_frame(offset_x, offset_y, frame)
        frames.append(new_frame)
    middle_offset_x = (img_width - target_width) // 2
    right_offset_x = img_width - target_width
    for i in range(half_frames):
        offset_x = right_offset_x - int(((right_offset_x - middle_offset_x) / half_frames) * i)
        offset_y = 0
        offset_x = max(0, min(offset_x, img_width - target_width))
        frame = image_clip.get_frame((half_frames + i) / fps)
        new_frame = create_frame(offset_x, offset_y, frame)
        frames.append(new_frame)
    video_clip = ImageSequenceClip(frames, fps=fps)
    video_clip = video_clip.with_audio(audio_clip)
    video_clip.write_videofile(output_path, fps=fps, codec='libx264', audio_codec='aac', threads=2, logger=None)


def create_left_to_right_video(image_path, audio_path, output_path, height=1024, width=768, fps=24):
    image_clip = ImageClip(image_path)
    audio_clip = AudioFileClip(audio_path)
    img_width, img_height = image_clip.size
    assert img_width == 1024 and img_height == 1024, "图像尺寸必须是 1024x1024"
    target_height = height
    target_width = width
    frames = []
    third_duration = audio_clip.duration
    for t in np.linspace(0, third_duration, int(third_duration * fps)):
        offset_x = int((img_width / third_duration) * t)
        offset_y = 0
        if offset_x >= (img_width - target_width):
            break
        frame = image_clip.get_frame(t)
        new_frame = np.zeros((target_height, target_width, 3), dtype=np.uint8)
        paste_height = min(target_height, img_height - offset_y)
        paste_width = min(target_width, img_width - offset_x)
        paste_x = 0
        paste_y = 0
        new_frame[paste_y:paste_y + paste_height, paste_x:paste_x + paste_width, :] = frame[
                                                                                      offset_y:offset_y + paste_height,
                                                                                      offset_x:offset_x + paste_width,
                                                                                      :]

        frames.append(new_frame)
    video_clip = ImageSequenceClip(frames, fps=fps)
    video_clip = video_clip.with_audio(audio_clip)
    video_clip.write_videofile(output_path, fps=fps, codec='libx264', audio_codec='aac', threads=2, logger=None)


def create_left_to_right_to_left_video(image_path, audio_path, output_path, height=1024, width=768, fps=24):
    image_clip = ImageClip(image_path)
    audio_clip = AudioFileClip(audio_path)
    img_width, img_height = image_clip.size
    assert img_width == 1024 and img_height == 1024, "图像尺寸必须是 1024x1024"
    target_height = height
    target_width = width
    frames = []
    total_frames = int(audio_clip.duration * fps)
    for i in range(total_frames):
        if i < total_frames // 2:
            offset_x = int((img_width - target_width) / (total_frames // 2) * i)
        else:
            offset_x = (img_width - target_width) - int(
                (img_width - target_width) / (total_frames // 2) * (i - total_frames // 2))
        offset_y = 0
        offset_x = max(0, min(offset_x, img_width - target_width))
        frame = image_clip.get_frame(i / fps)
        new_frame = np.zeros((target_height, target_width, 3), dtype=np.uint8)
        paste_height = min(target_height, img_height - offset_y)
        paste_width = min(target_width, img_width - offset_x)
        paste_x = 0
        paste_y = 0
        new_frame[paste_y:paste_y + paste_height, paste_x:paste_x + paste_width, :] = frame[
                                                                                      offset_y:offset_y + paste_height,
                                                                                      offset_x:offset_x + paste_width,
                                                                                      :]

        frames.append(new_frame)
    video_clip = ImageSequenceClip(frames, fps=fps)
    video_clip = video_clip.with_audio(audio_clip)
    video_clip.write_videofile(output_path, fps=fps, codec='libx264', audio_codec='aac', threads=2, logger=None)


def create_left_to_right_and_center_and_zoom_video(image_path, audio_path, output_path, height=1024, width=768, fps=24):
    image_clip = ImageClip(image_path)
    audio_clip = AudioFileClip(audio_path)
    img_width, img_height = image_clip.size
    assert img_width == 1024 and img_height == 1024, "图像尺寸必须是 1024x1024"
    target_height = height
    target_width = width
    frames = []
    total_frames = int(audio_clip.duration * fps)
    third_duration = total_frames // 3
    for i in range(third_duration):
        offset_x = int((img_width - target_width) / third_duration * i)
        offset_y = 0
        offset_x = max(0, min(offset_x, img_width - target_width))
        frame = image_clip.get_frame(i / fps)
        new_frame = np.zeros((target_height, target_width, 3), dtype=np.uint8)
        paste_height = min(target_height, img_height - offset_y)
        paste_width = min(target_width, img_width - offset_x)
        paste_x = 0
        paste_y = 0
        new_frame[paste_y:paste_y + paste_height, paste_x:paste_x + paste_width, :] = frame[
                                                                                      offset_y:offset_y + paste_height,
                                                                                      offset_x:offset_x + paste_width,
                                                                                      :]
        frames.append(new_frame)
    middle_offset_x = (img_width - target_width) // 2
    right_offset_x = img_width - target_width
    for i in range(third_duration):
        offset_x = right_offset_x - int(((right_offset_x - middle_offset_x) / third_duration) * i)
        offset_y = 0
        offset_x = max(0, min(offset_x, img_width - target_width))
        frame = image_clip.get_frame((third_duration + i) / fps)
        new_frame = np.zeros((target_height, target_width, 3), dtype=np.uint8)
        paste_height = min(target_height, img_height - offset_y)
        paste_width = min(target_width, img_width - offset_x)
        paste_x = 0
        paste_y = 0
        new_frame[paste_y:paste_y + paste_height, paste_x:paste_x + paste_width, :] = frame[
                                                                                      offset_y:offset_y + paste_height,
                                                                                      offset_x:offset_x + paste_width,
                                                                                      :]
        frames.append(new_frame)
    initial_frame = frames[-1]
    for i in range(third_duration):
        scale = 1 + (i / third_duration) * 0.2
        new_width = int(target_width * scale)
        new_height = int(target_height * scale)
        offset_x = (new_width - target_width) // 2
        offset_y = (new_height - target_height) // 2
        frame = initial_frame
        frame = np.array(Image.fromarray(frame).resize((new_width, new_height), Image.LANCZOS))
        new_frame = np.zeros((target_height, target_width, 3), dtype=np.uint8)
        paste_height = min(target_height, new_height - offset_y)
        paste_width = min(target_width, new_width - offset_x)
        paste_x = max(0, (target_width - paste_width) // 2)
        start_paste_y = int(target_height * 0.8)
        end_paste_y = 0
        paste_y = start_paste_y - int(start_paste_y * (i / third_duration))
        paste_y = max(0, min(paste_y, target_height - paste_height))
        new_frame[paste_y:paste_y + paste_height, paste_x:paste_x + paste_width, :] = frame[
                                                                                      offset_y:offset_y + paste_height,
                                                                                      offset_x:offset_x + paste_width,
                                                                                      :]
        frames.append(new_frame)
    video_clip = ImageSequenceClip(frames, fps=fps)
    video_clip = video_clip.with_audio(audio_clip)
    video_clip.write_videofile(output_path, fps=fps, codec='libx264', audio_codec='aac', threads=2, logger=None)


def create_left_to_right_and_center_and_top_zoom_video(image_path, audio_path, output_path, height=1024, width=768,
                                                       fps=24):
    image_clip = ImageClip(image_path)
    audio_clip = AudioFileClip(audio_path)
    img_width, img_height = image_clip.size
    assert img_width == 1024 and img_height == 1024, "图像尺寸必须是 1024x1024"
    target_height = height
    target_width = width
    frames = []
    total_frames = int(audio_clip.duration * fps)  # 总帧数
    third_duration = total_frames // 3
    for i in range(third_duration):
        offset_x = int((img_width - target_width) / third_duration * i)
        offset_y = 0
        offset_x = max(0, min(offset_x, img_width - target_width))
        frame = image_clip.get_frame(i / fps)
        new_frame = np.zeros((target_height, target_width, 3), dtype=np.uint8)
        paste_height = min(target_height, img_height - offset_y)
        paste_width = min(target_width, img_width - offset_x)
        paste_x = 0
        paste_y = 0
        new_frame[paste_y:paste_y + paste_height, paste_x:paste_x + paste_width, :] = frame[
                                                                                      offset_y:offset_y + paste_height,
                                                                                      offset_x:offset_x + paste_width,
                                                                                      :]
        frames.append(new_frame)
    middle_offset_x = (img_width - target_width) // 2
    right_offset_x = img_width - target_width
    for i in range(third_duration):
        offset_x = right_offset_x - int(((right_offset_x - middle_offset_x) / third_duration) * i)
        offset_y = 0
        offset_x = max(0, min(offset_x, img_width - target_width))
        frame = image_clip.get_frame((third_duration + i) / fps)
        new_frame = np.zeros((target_height, target_width, 3), dtype=np.uint8)
        paste_height = min(target_height, img_height - offset_y)
        paste_width = min(target_width, img_width - offset_x)
        paste_x = 0
        paste_y = 0
        new_frame[paste_y:paste_y + paste_height, paste_x:paste_x + paste_width, :] = frame[
                                                                                      offset_y:offset_y + paste_height,
                                                                                      offset_x:offset_x + paste_width,
                                                                                      :]
        frames.append(new_frame)
    initial_frame = frames[-1]
    for i in range(third_duration):
        scale = 1 + (i / third_duration) * 1
        new_width = int(target_width * scale)
        new_height = int(target_height * scale)
        offset_x = (new_width - target_width) // 2
        offset_y = (new_height - target_height) // 2
        frame = initial_frame
        frame = np.array(Image.fromarray(frame).resize((new_width, new_height), Image.LANCZOS))
        new_frame = np.zeros((target_height, target_width, 3), dtype=np.uint8)
        paste_height = min(target_height, new_height - offset_y)
        paste_width = min(target_width, new_width - offset_x)
        paste_x = max(0, (target_width - paste_width) // 2)
        paste_y = max(0, (target_height - paste_height) // 2)
        new_frame[paste_y:paste_y + paste_height, paste_x:paste_x + paste_width, :] = frame[
                                                                                      offset_y:offset_y + paste_height,
                                                                                      offset_x:offset_x + paste_width,
                                                                                      :]
        frames.append(new_frame)
    video_clip = ImageSequenceClip(frames, fps=fps)
    video_clip = video_clip.with_audio(audio_clip)
    video_clip.write_videofile(output_path, fps=fps, codec='libx264', audio_codec='aac', threads=2, logger=None)


def create_right_to_left_zoom_video(image_path, audio_path, output_path, zoom_factor=1.3, height=1024, width=768,
                                    fps=24):
    image_clip = ImageClip(image_path)
    audio_clip = AudioFileClip(audio_path)
    img_width, img_height = image_clip.size
    assert img_width == 1024 and img_height == 1024, "图像尺寸必须是 1024x1024"

    center_x = (img_width - width) // 2
    center_y = (img_height - height) // 2
    frames = []
    duration = audio_clip.duration
    for t in np.linspace(0, duration, int(duration * fps)):
        if t < duration / 2:
            move_x = int(t / (duration / 2) * center_x)
            move_y = 0
            scale = 1
            scaled_width = img_width
            scaled_height = img_height
        else:
            move_x = center_x
            scale = 1 + (t - duration / 2) / (duration / 2) * (zoom_factor - 1)
            scaled_width = int(img_width * scale)
            scaled_height = int(img_height * scale)
            max_move_y = height - scaled_height
            move_y = int((t - duration / 2) / (duration / 2) * max_move_y)
        left = move_x
        top = move_y
        right = left + width
        bottom = top + height
        frame = image_clip.get_frame(t)
        scaled_frame = np.array(Image.fromarray(frame).resize((scaled_width, scaled_height)))
        left_crop = max(0, (scaled_width - width) // 2 - move_x)
        top_crop = max(0, move_y)
        cropped_frame = scaled_frame[top_crop:top_crop + height, left_crop:left_crop + width]
        frames.append(cropped_frame)
    video_clip = ImageSequenceClip(frames, fps=fps)
    video_clip = video_clip.with_audio(audio_clip)
    video_clip.write_videofile(output_path, fps=fps, codec='libx264', audio_codec='aac', threads=2, logger=None)


def create_left_to_center_and_zoom_video(image_path, audio_path, output_path, height=1024, width=768, fps=24,
                                         zoom_factor=1.3):
    image_clip = ImageClip(image_path)
    audio_clip = AudioFileClip(audio_path)
    img_width, img_height = image_clip.size
    assert img_width == 1024 and img_height == 1024, "图像尺寸必须是 1024x1024"
    center_x = (img_width - width) // 2
    center_y = (img_height - height) // 2
    frames = []
    duration = audio_clip.duration
    for t in np.linspace(0, duration, int(duration * fps)):
        if t < duration / 2:
            move_x = int(t / (duration / 2) * center_x)
            move_y = 0
            scale = 1
        else:
            move_x = center_x
            move_y = int((t - duration / 2) / (duration / 2) * (img_height - height))
            scale = 1 + (t - duration / 2) / (duration / 2) * (zoom_factor - 1)
        left = move_x
        top = move_y
        right = left + width
        bottom = top + height
        frame = image_clip.get_frame(t)
        cropped_frame = np.array(Image.fromarray(frame).crop((left, top, right, bottom)))
        new_width = int(width * scale)
        new_height = int(height * scale)
        frame_resized = np.array(Image.fromarray(cropped_frame).resize((new_width, new_height)))
        left_resize = (new_width - width) // 2
        top_resize = (new_height - height) // 2
        resized_frame = frame_resized[top_resize:top_resize + height, left_resize:left_resize + width]
        frames.append(resized_frame)
    video_clip = ImageSequenceClip(frames, fps=fps)
    video_clip = video_clip.with_audio(audio_clip)
    video_clip.write_videofile(output_path, fps=fps, codec='libx264', audio_codec='aac', threads=2, logger=None)


def create_zoom_to_top_video(image_path, audio_path, output_path, height=1024, width=768, fps=24,
                             zoom_factor=1.5):
    image_clip = ImageClip(image_path)
    audio_clip = AudioFileClip(audio_path)
    img_width, img_height = image_clip.size
    assert img_width == 1024 and img_height == 1024, "图像尺寸必须是 1024x1024"
    center_x = (img_width - width) // 2
    center_y = (img_height - height) // 2
    frames = []
    final_move_x = None
    final_move_y = None
    final_scale = None
    duration = audio_clip.duration
    for t in np.linspace(0, duration, int(duration * fps), endpoint=False):
        if t < duration / 2:
            move_x = int(t / (duration / 2) * center_x)
            move_y = 0
            scale = 1 + (t / (duration / 2)) * (zoom_factor - 1)
            final_move_x = move_x
            final_move_y = move_y
            final_scale = scale
        else:
            if final_move_x is None or final_move_y is None or final_scale is None:
                raise ValueError("第一阶段的状态未正确初始化！")
            move_x = final_move_x
            total_move_y_distance = (img_height - height * final_scale) - final_move_y + 340
            move_y = final_move_y + int((t - duration / 2) / (duration / 2) * total_move_y_distance)
            scale = final_scale
        left = move_x
        top = move_y
        right = left + width
        bottom = top + height
        frame = image_clip.get_frame(t)
        cropped_frame = np.array(Image.fromarray(frame).crop((left, top, right, bottom)))
        new_width = int(width * scale)
        new_height = int(height * scale)
        frame_resized = np.array(Image.fromarray(cropped_frame).resize((new_width, new_height)))
        left_resize = (new_width - width) // 2
        top_resize = (new_height - height) // 2
        resized_frame = frame_resized[top_resize:top_resize + height, left_resize:left_resize + width]
        frames.append(resized_frame)
    video_clip = ImageSequenceClip(frames, fps=fps)
    video_clip = video_clip.with_audio(audio_clip)
    video_clip.write_videofile(output_path, fps=fps, codec='libx264', audio_codec='aac', threads=2, logger=None)


def random_scroll_animation():
    animations = [
        lambda image_path, audio_path, output_path: create_left_to_right_and_center_video(image_path, audio_path,
                                                                                          output_path),
        lambda image_path, audio_path, output_path: create_left_to_right_video(image_path, audio_path, output_path),
        lambda image_path, audio_path, output_path: create_left_to_right_to_left_video(image_path, audio_path,
                                                                                       output_path),
        lambda image_path, audio_path, output_path: create_left_to_right_and_center_and_zoom_video(image_path,
                                                                                                   audio_path,
                                                                                                   output_path),
        lambda image_path, audio_path, output_path: create_left_to_right_and_center_and_top_zoom_video(image_path,
                                                                                                       audio_path,
                                                                                                       output_path),
        lambda image_path, audio_path, output_path: create_right_to_left_zoom_video(image_path, audio_path,
                                                                                    output_path),
        lambda image_path, audio_path, output_path: create_left_to_center_and_zoom_video(image_path, audio_path,
                                                                                         output_path),
        lambda image_path, audio_path, output_path: create_zoom_to_top_video(image_path, audio_path, output_path),
    ]
    return random.choice(animations)
