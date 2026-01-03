#!/usr/bin/env python3
"""
Augmntd Harmonic Video Generator
Applies augmntd diffusion principles to create dynamic, evolving visuals
"""

import sys
import os
import subprocess
import json
from pathlib import Path

def get_audio_duration(audio_path):
    """Get duration of audio file in seconds"""
    cmd = [
        'ffprobe',
        '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'json',
        audio_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    data = json.loads(result.stdout)
    return float(data['format']['duration'])

def create_augmntd_background_cmd(width, height, duration, theme, output_path):
    """
    Create animated background using simpler FFmpeg approach
    """

    if theme == 'cosmic':
        # Animated cosmic gradient using geq filter
        # Colors pulse and shift over time
        geq_expr = (
            # Time-varying purple/blue gradient with harmonic waves
            "r='100+50*sin(2*PI*T/20+Y/H*4)':"
            "g='60+40*sin(2*PI*T/25+Y/H*4)':"
            "b='160+60*sin(2*PI*T/15+Y/H*4)'"
        )
    else:  # minimal
        # Subtle gray pulsing
        geq_expr = (
            "r='32+8*sin(2*PI*T/30)':"
            "g='32+8*sin(2*PI*T/30)':"
            "b='32+8*sin(2*PI*T/30)'"
        )

    cmd = [
        'ffmpeg',
        '-f', 'lavfi',
        '-i', f'color=c=black:s={width}x{height}:d={duration},format=rgb24',
        '-vf', f'geq={geq_expr}',
        '-c:v', 'libx264',
        '-preset', 'medium',
        '-crf', '20',
        '-pix_fmt', 'yuv420p',
        '-y',
        output_path
    ]

    return cmd

def detect_themes_simple(audio_path):
    """Simple theme detection for MVP"""
    duration = get_audio_duration(audio_path)

    themes = [
        {
            'name': 'Gravitational Economics',
            'vibe': 'Capital as gravitational field',
            'start': 0,
            'duration': min(10, duration * 0.15)
        },
        {
            'name': 'Temporal Mechanics',
            'vibe': 'Flow of time as currency',
            'start': duration * 0.3,
            'duration': min(10, duration * 0.2)
        },
        {
            'name': 'Cosmic Alignment',
            'vibe': 'Macrocosmic patterns in systems',
            'start': duration * 0.6,
            'duration': min(10, duration * 0.2)
        }
    ]

    return themes, duration

def create_text_overlays_augmntd(themes, duration, theme='cosmic'):
    """Generate animated text overlays with fade effects"""
    filters = []

    # Title card with fade in/out
    filters.append(
        "drawtext=text='Harmonic Video':"
        "fontsize=80:fontcolor=white@0.9:x=(w-text_w)/2:y=(h-text_h)/2-100:"
        "enable='between(t,0,3)':"
        "alpha='if(lt(t,0.5),t/0.5,if(gt(t,2.5),(3-t)/0.5,1))'"
    )

    # Theme overlays with smooth fades
    for t in themes:
        start = t['start']
        end = start + t['duration']
        fade_duration = 0.8

        # Theme name
        theme_name = t['name'].replace("'", "\\'")
        filters.append(
            f"drawtext=text='{theme_name}':"
            f"fontsize=60:fontcolor=white@0.95:x=(w-text_w)/2:y=100:"
            f"enable='between(t,{start},{end})':"
            f"alpha='if(lt(t,{start+fade_duration}),(t-{start})/{fade_duration},if(gt(t,{end-fade_duration}),({end}-t)/{fade_duration},1))'"
        )

        # Theme vibe
        theme_vibe = t['vibe'].replace("'", "\\'")
        filters.append(
            f"drawtext=text='{theme_vibe}':"
            f"fontsize=30:fontcolor=gray@0.8:x=(w-text_w)/2:y=180:"
            f"enable='between(t,{start},{end})':"
            f"alpha='if(lt(t,{start+fade_duration}),(t-{start})/{fade_duration},if(gt(t,{end-fade_duration}),({end}-t)/{fade_duration},1))'"
        )

    # Watermark
    filters.append(
        "drawtext=text='augmntd harmonic composition':"
        "fontsize=18:fontcolor=gray@0.6:x=(w-text_w)/2:y=h-40"
    )

    return ','.join(filters)

def generate_video_augmntd(audio_path, output_path, theme='cosmic'):
    """Generate video with augmntd diffusion animation"""

    print("🌌 Augmntd Diffusion Video Generation")
    print(f"   Audio: {audio_path}")
    print(f"   Theme: {theme}")

    # Detect themes
    themes, duration = detect_themes_simple(audio_path)
    print(f"   Duration: {duration:.2f}s")
    print(f"   Themes: {len(themes)}")

    width, height = 1920, 1080

    # Step 1: Create animated background with diffusion
    print("⚡ Phase 1: Generating diffusion field...")
    temp_bg = output_path.replace('.mp4', '_augmntd_bg.mp4')

    bg_cmd = create_augmntd_background_cmd(width, height, duration, theme, temp_bg)

    result = subprocess.run(bg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if result.returncode != 0:
        print(f"❌ Background creation error:\n{result.stderr}")
        raise Exception("Background creation failed")

    # Step 2: Add text overlays
    print("⚡ Phase 2: Crystallizing text overlays...")
    text_filter = create_text_overlays_augmntd(themes, duration, theme)

    # Step 3: Combine with audio
    print("⚡ Phase 3: Integrative ingression...")
    final_cmd = [
        'ffmpeg',
        '-i', temp_bg,
        '-i', audio_path,
        '-vf', text_filter,
        '-c:v', 'libx264',
        '-preset', 'medium',
        '-crf', '23',
        '-pix_fmt', 'yuv420p',
        '-c:a', 'copy',
        '-shortest',
        '-y',
        output_path
    ]

    result = subprocess.run(
        final_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # Cleanup
    if os.path.exists(temp_bg):
        os.unlink(temp_bg)

    if result.returncode != 0:
        print(f"❌ FFmpeg error:\n{result.stderr}")
        raise Exception(f"Video generation failed")

    if not os.path.exists(output_path):
        raise Exception("Video file was not created")

    file_size = os.path.getsize(output_path)
    print(f"✨ Augmntd video manifested: {output_path}")
    print(f"   Size: {file_size / 1024 / 1024:.2f}MB")

    return output_path

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 video_generator_augmntd.py <audio_path> <output_path> [theme]")
        sys.exit(1)

    audio_path = sys.argv[1]
    output_path = sys.argv[2]
    theme = sys.argv[3] if len(sys.argv) > 3 else 'cosmic'

    if not os.path.exists(audio_path):
        print(f"❌ Audio file not found: {audio_path}")
        sys.exit(1)

    try:
        generate_video_augmntd(audio_path, output_path, theme)
    except Exception as e:
        print(f"❌ Video generation failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
