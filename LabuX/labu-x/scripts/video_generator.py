#!/usr/bin/env python3
"""
Harmonic Video Generator - MVP
Generates videos from audio files with harmonic theme overlays
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

def create_cosmic_gradient(width=1920, height=1080, theme='cosmic'):
    """Create FFmpeg filter for cosmic gradient background"""
    if theme == 'cosmic':
        # Purple to blue gradient with stars
        return (
            f"color=c=0x1a1a2e:s={width}x{height}:d=1[bg];"
            f"[bg]drawbox=x=0:y=0:w={width}:h={height}:"
            f"color=0x6a11cb@0.5:t=fill[bg1];"
            f"[bg1]drawbox=x=0:y=ih/2:w={width}:h={height}/2:"
            f"color=0x2575fc@0.5:t=fill[bg2];"
            f"[bg2]geq=lum='random(1)*255':cb=128:cr=128[stars];"
            f"[stars]fade=in:st=0:d=0.5"
        )
    else:  # minimal
        # Clean dark gradient
        return (
            f"color=c=0x0f0f0f:s={width}x{height}:d=1[bg];"
            f"[bg]drawbox=x=0:y=0:w={width}:h={height}:"
            f"color=0x1f1f1f@0.7:t=fill[bg1];"
            f"[bg1]fade=in:st=0:d=0.5"
        )

def detect_themes_simple(audio_path):
    """
    Simple theme detection for MVP
    In production, this would call harmonic_composer.py
    For now, returns default themes
    """
    duration = get_audio_duration(audio_path)

    # Default themes for MVP
    themes = [
        {
            'name': 'Gravitational Economics',
            'vibe': 'Capital as gravitational field',
            'start': 0,
            'duration': min(10, duration)
        },
        {
            'name': 'Temporal Mechanics',
            'vibe': 'Flow of time as currency',
            'start': min(10, duration * 0.3),
            'duration': min(10, duration * 0.3)
        },
        {
            'name': 'Cosmic Alignment',
            'vibe': 'Macrocosmic patterns in systems',
            'start': min(duration * 0.6, duration - 10),
            'duration': min(10, duration * 0.2)
        }
    ]

    return themes, duration

def create_text_overlays(themes, duration, theme='cosmic'):
    """Generate FFmpeg drawtext filters for theme overlays"""
    filters = []

    # Title card at start (simplified - no emoji, proper escaping)
    title_color = 'white' if theme == 'cosmic' else 'white'
    filters.append(
        f"drawtext=text='Harmonic Video':"
        f"fontsize=80:fontcolor={title_color}:x=(w-text_w)/2:y=(h-text_h)/2-100:"
        f"enable='between(t,0,3)'"
    )

    # Theme overlays
    for i, t in enumerate(themes):
        start = t['start']
        end = start + t['duration']

        # Theme name - escape single quotes properly
        theme_name = t['name'].replace("'", "\\'")
        filters.append(
            f"drawtext=text='{theme_name}':"
            f"fontsize=60:fontcolor=white:x=(w-text_w)/2:y=100:"
            f"enable='between(t,{start},{end})'"
        )

        # Theme vibe
        theme_vibe = t['vibe'].replace("'", "\\'")
        filters.append(
            f"drawtext=text='{theme_vibe}':"
            f"fontsize=30:fontcolor=gray:x=(w-text_w)/2:y=180:"
            f"enable='between(t,{start},{end})'"
        )

    # Watermark
    filters.append(
        f"drawtext=text='Made with Harmonic Composer':"
        f"fontsize=20:fontcolor=gray:x=(w-text_w)/2:y=h-40"
    )

    return ','.join(filters)

def generate_video(audio_path, output_path, theme='cosmic'):
    """Generate video with harmonic theme overlays"""

    print("🎬 Starting video generation...")
    print(f"   Audio: {audio_path}")
    print(f"   Theme: {theme}")

    # Detect themes (simplified for MVP)
    themes, duration = detect_themes_simple(audio_path)
    print(f"   Duration: {duration:.2f}s")
    print(f"   Themes: {len(themes)}")

    # Create video with FFmpeg
    width, height = 1920, 1080

    # Step 1: Create background video with correct duration
    temp_bg = output_path.replace('.mp4', '_bg.mp4')

    # Choose background colors based on theme
    if theme == 'cosmic':
        color1, color2 = '0x1a1a2e', '0x2575fc'
    else:
        color1, color2 = '0x0f0f0f', '0x1f1f1f'

    # Create gradient background for full duration
    bg_cmd = [
        'ffmpeg',
        '-f', 'lavfi',
        '-i', f'color=c={color1}:s={width}x{height}:d={duration},format=yuv420p',
        '-vf', f'drawbox=x=0:y=ih/2:w={width}:h={height}/2:color={color2}@0.6:t=fill',
        '-c:v', 'libx264',
        '-preset', 'ultrafast',
        '-y',
        temp_bg
    ]

    print("⚡ Creating background...")
    result = subprocess.run(bg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if result.returncode != 0:
        print(f"❌ Background creation error:\n{result.stderr}")
        raise Exception("Background creation failed")

    # Step 2: Add text overlays
    text_filter = create_text_overlays(themes, duration, theme)

    # Step 3: Combine background, text overlays, and audio
    final_cmd = [
        'ffmpeg',
        '-i', temp_bg,
        '-i', audio_path,
        '-vf', text_filter,  # Use -vf instead of -filter_complex for single video input
        '-c:v', 'libx264',
        '-preset', 'medium',
        '-crf', '23',
        '-pix_fmt', 'yuv420p',
        '-c:a', 'copy',  # Copy audio instead of re-encoding
        '-shortest',
        '-y',
        output_path
    ]

    print("⚡ Adding text overlays and audio...")
    result = subprocess.run(
        final_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # Cleanup temp background
    if os.path.exists(temp_bg):
        os.unlink(temp_bg)

    if result.returncode != 0:
        print(f"❌ FFmpeg error:\n{result.stderr}")
        raise Exception(f"FFmpeg failed with code {result.returncode}")

    # Check output file exists
    if not os.path.exists(output_path):
        raise Exception("Video file was not created")

    file_size = os.path.getsize(output_path)
    print(f"✅ Video generated: {output_path}")
    print(f"   Size: {file_size / 1024 / 1024:.2f}MB")

    return output_path

def main():
    if len(sys.argv) < 3:
        print("Usage: python video_generator.py <audio_path> <output_path> [theme]")
        sys.exit(1)

    audio_path = sys.argv[1]
    output_path = sys.argv[2]
    theme = sys.argv[3] if len(sys.argv) > 3 else 'cosmic'

    if not os.path.exists(audio_path):
        print(f"❌ Audio file not found: {audio_path}")
        sys.exit(1)

    try:
        generate_video(audio_path, output_path, theme)
    except Exception as e:
        print(f"❌ Video generation failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
