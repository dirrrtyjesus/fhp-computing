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
    Create AMPLIFIED animated background inspired by augmntd diffusion aesthetic:
    - Golden data particles
    - Purple cosmic nebulae
    - Spiral vortex patterns
    - Luminous glow effects
    """

    if theme == 'cosmic':
        # COSMIC: Purple nebulae + golden particles + spiral vortex
        # Layer 1: Deep purple/blue cosmic gradient with movement
        base_gradient = (
            "r='60+45*sin(2*PI*T/18+Y/H*5+X/W*2)':"
            "g='25+20*sin(2*PI*T/22+Y/H*5)':"  # Reduced green
            "b='130+90*sin(2*PI*T/14+Y/H*5-X/W)'"  # Increased blue
        )

        # Layer 2: Golden particles (data streams) - more subtle
        golden_particles = (
            # Sparse bright golden particles
            "r='if(lt(random(0)*255,5),clip(r(X,Y)+140,0,255),r(X,Y))':"  # Add gold to existing
            "g='if(lt(random(0)*255,5),clip(g(X,Y)+100,0,255),g(X,Y))':"  # Medium gold
            "b='if(lt(random(0)*255,5),clip(b(X,Y)+20,0,255),b(X,Y))'"  # Low blue for gold
        )

        # Layer 3: Spiral vortex (gravitational well effect) - balanced colors
        spiral_vortex = (
            # Radial distance and angle calculations create spiral
            "r='clip(r(X,Y)+30*sin(atan2(Y-H/2,X-W/2)*3+hypot(X-W/2,Y-H/2)/80-T*1.5),0,255)':"
            "g='clip(g(X,Y)+15*sin(atan2(Y-H/2,X-W/2)*3+hypot(X-W/2,Y-H/2)/100-T*1.2),0,255)':"  # Less green
            "b='clip(b(X,Y)+50*sin(atan2(Y-H/2,X-W/2)*3+hypot(X-W/2,Y-H/2)/60-T*2),0,255)'"  # More blue
        )

        # Layer 4: Pulsing vignette (event horizon feel) - darker edges
        vignette = (
            "r='r(X,Y)*(1-0.5*(1-exp(-0.0000008*hypot(X-W/2,Y-H/2)^2))*(0.7+0.3*sin(2*PI*T/25)))':"
            "g='g(X,Y)*(1-0.6*(1-exp(-0.0000008*hypot(X-W/2,Y-H/2)^2))*(0.7+0.3*sin(2*PI*T/25)))':"  # Darken green more
            "b='b(X,Y)*(1-0.4*(1-exp(-0.0000008*hypot(X-W/2,Y-H/2)^2))*(0.7+0.3*sin(2*PI*T/25)))'"
        )

        # Combine all layers with stronger glow for golden particles
        filter_chain = f'geq={base_gradient},geq={golden_particles},geq={spiral_vortex},geq={vignette},gblur=sigma=2.5'

    else:  # minimal
        # MINIMAL: Subtle pulsing with gentle particle hints
        base_gradient = (
            "r='40+16*sin(2*PI*T/30)':"
            "g='40+16*sin(2*PI*T/30)':"
            "b='42+18*sin(2*PI*T/30)'"
        )

        minimal_particles = (
            "r='if(lt(random(0)*255,3),120,r(X,Y))':"
            "g='if(lt(random(0)*255,3),120,g(X,Y))':"
            "b='if(lt(random(0)*255,3),130,b(X,Y))'"
        )

        filter_chain = f'geq={base_gradient},geq={minimal_particles},gblur=sigma=1'

    cmd = [
        'ffmpeg',
        '-f', 'lavfi',
        '-i', f'color=c=black:s={width}x{height}:d={duration},format=rgb24',
        '-vf', filter_chain,
        '-c:v', 'libx264',
        '-preset', 'medium',
        '-crf', '18',  # Higher quality for glow effects
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
    """
    Generate AMPLIFIED text overlays with golden glow effects
    Inspired by luminous data streams aesthetic
    """
    filters = []

    if theme == 'cosmic':
        title_color = '#FFD700'  # Gold
        subtitle_color = '#DDA0DD'  # Plum/purple
        shadow_color = '#6A11CB'  # Deep purple glow
    else:
        title_color = 'white'
        subtitle_color = 'gray'
        shadow_color = 'black'

    # Epic title card with golden glow and pulsing
    filters.append(
        f"drawtext=text='HARMONIC VIDEO':"
        f"fontsize='75+15*sin(2*PI*t/2.5)':"  # Pulsing size
        f"fontcolor={title_color}@0.98:"
        "x='(w-text_w)/2':"
        "y='(h-text_h)/2-110+8*sin(2*PI*t/1.5)':"  # Floating
        "enable='between(t,0,4)':"
        "alpha='if(lt(t,0.8),t/0.8,if(gt(t,3.2),(4-t)/0.8,1))':"
        f"shadowcolor={shadow_color}@0.8:shadowx=3:shadowy=3"
    )

    # Subtitle with purple glow
    filters.append(
        f"drawtext=text='augmntd diffusion composition':"
        f"fontsize=26:"
        f"fontcolor={subtitle_color}@0.85:"
        "x='(w-text_w)/2':"
        "y='(h-text_h)/2-50':"
        "enable='between(t,0.5,4)':"
        "alpha='if(lt(t,1),(t-0.5)/0.5,if(gt(t,3.5),(4-t)/0.5,1))':"
        "shadowcolor=black@0.7:shadowx=2:shadowy=2"
    )

    # Theme overlays with golden glow
    for t in themes:
        start = t['start']
        end = start + t['duration']
        fade_duration = 1.0

        # Theme name - GOLDEN and glowing
        theme_name = t['name'].replace("'", "\\'")
        filters.append(
            f"drawtext=text='{theme_name}':"
            f"fontsize='68+12*sin(2*PI*t/3)':"  # Pulsing
            f"fontcolor={title_color}@0.98:"
            "x='(w-text_w)/2':"
            "y='70+6*sin(2*PI*t/2)':"  # Floating
            f"enable='between(t,{start},{end})':"
            f"alpha='if(lt(t,{start+fade_duration}),(t-{start})/{fade_duration},if(gt(t,{end-fade_duration}),({end}-t)/{fade_duration},1))':"
            f"shadowcolor={shadow_color}@0.9:shadowx=4:shadowy=4"
        )

        # Theme vibe - Purple accent
        theme_vibe = t['vibe'].replace("'", "\\'")
        filters.append(
            f"drawtext=text='{theme_vibe}':"
            f"fontsize=34:"
            f"fontcolor={subtitle_color}@0.9:"
            "x='(w-text_w)/2':"
            "y=160:"
            f"enable='between(t,{start},{end})':"
            f"alpha='if(lt(t,{start+fade_duration}),(t-{start})/{fade_duration},if(gt(t,{end-fade_duration}),({end}-t)/{fade_duration},1))':"
            "shadowcolor=black@0.7:shadowx=2:shadowy=2"
        )

    # Watermark with subtle pulse
    filters.append(
        f"drawtext=text='augmntd harmonic composition':"
        f"fontsize='17+2*sin(2*PI*t/8)':"
        f"fontcolor={subtitle_color}@0.5:"
        "x='(w-text_w)/2':"
        "y='h-45'"
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
