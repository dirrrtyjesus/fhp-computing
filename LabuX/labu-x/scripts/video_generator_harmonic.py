#!/usr/bin/env python3
"""
Harmonic Augmntd Diffusion Video Generator
Fuses harmonic_composer analysis with visual generation
The detected themes and resonances DRIVE the visual effects
"""

import sys
import os
import subprocess
import json
import re
from pathlib import Path

def run_harmonic_analysis(audio_path):
    """
    Run harmonic_composer.py to detect themes
    Returns parsed themes with resonance data
    """
    print("🔍 Phase 0: Harmonic Analysis - Detecting resonant themes...")

    # Run harmonic composer
    composer_script = Path(__file__).parent / "harmonic_composer.py"
    result = subprocess.run(
        ['python3', str(composer_script), audio_path],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"⚠️  Harmonic analysis failed, using default themes")
        return None

    # Parse output to extract themes
    themes = parse_harmonic_output(result.stdout)
    print(f"✅ Detected {len(themes)} harmonic themes")

    return themes

def parse_harmonic_output(output):
    """
    Parse harmonic_composer.py output to extract themes with metadata
    """
    themes = []

    # Pattern to match theme sections
    theme_pattern = r'={70}\n✨ (.+?)\n={70}\nResonance Strength: (█+)'
    vibe_pattern = r'Core Vibe: (.+?)(?:\n|$)'
    expanded_pattern = r'🌊 EXPANDED COMPOSITION:\n-{70}\n\n(.+?)(?:\n\n\n|$)'

    # Find all themes
    for match in re.finditer(theme_pattern, output, re.MULTILINE):
        theme_name = match.group(1)
        resonance_bars = len(match.group(2))

        # Find corresponding vibe and expanded text
        section_start = match.end()
        section_text = output[section_start:section_start+2000]

        vibe_match = re.search(vibe_pattern, section_text)
        expanded_match = re.search(expanded_pattern, section_text, re.DOTALL)

        theme = {
            'name': theme_name,
            'resonance': resonance_bars,  # 1-4 bars
            'vibe': vibe_match.group(1) if vibe_match else '',
            'expanded_text': expanded_match.group(1).strip() if expanded_match else '',
        }

        themes.append(theme)

    return themes

def map_theme_to_visuals(theme_name, resonance):
    """
    Map detected themes to specific visual characteristics
    """

    # Theme-specific color palettes
    theme_palettes = {
        'GRAVITATIONAL ECONOMICS': {
            'base_r': 80, 'base_g': 40, 'base_b': 140,  # Deep purple
            'accent_r': 200, 'accent_g': 150, 'accent_b': 50,  # Gold
            'particle_density': 8,
            'vortex_intensity': 1.5,
        },
        'TEMPORAL MECHANICS': {
            'base_r': 40, 'base_g': 60, 'base_b': 180,  # Blue
            'accent_r': 150, 'accent_g': 200, 'accent_b': 255,  # Cyan
            'particle_density': 6,
            'vortex_intensity': 1.2,
        },
        'COSMIC ALIGNMENT': {
            'base_r': 60, 'base_g': 30, 'base_b': 120,  # Dark purple
            'accent_r': 255, 'accent_g': 200, 'accent_b': 100,  # Bright gold
            'particle_density': 10,
            'vortex_intensity': 2.0,
        },
        'HARMONIC RESONANCE': {
            'base_r': 120, 'base_g': 50, 'base_b': 150,  # Purple-pink
            'accent_r': 255, 'accent_g': 150, 'accent_b': 200,  # Pink
            'particle_density': 7,
            'vortex_intensity': 1.3,
        },
        'GOLDEN RATIO': {
            'base_r': 90, 'base_g': 60, 'base_b': 30,  # Brown-gold
            'accent_r': 255, 'accent_g': 215, 'accent_b': 0,  # Pure gold
            'particle_density': 12,
            'vortex_intensity': 1.618,  # φ!
        },
    }

    # Find matching theme (partial match)
    visuals = {
        'base_r': 60, 'base_g': 30, 'base_b': 130,  # Default purple
        'accent_r': 200, 'accent_g': 180, 'accent_b': 80,  # Default gold
        'particle_density': 5,
        'vortex_intensity': 1.0,
    }

    for key, palette in theme_palettes.items():
        if key in theme_name.upper():
            visuals = palette
            break

    # Scale by resonance strength (1-4 bars)
    visuals['particle_density'] = int(visuals['particle_density'] * (resonance / 2))
    visuals['vortex_intensity'] *= (resonance / 2)

    return visuals

def distribute_themes_over_duration(themes, duration):
    """
    Distribute detected themes evenly across video duration
    """
    if not themes:
        return []

    theme_duration = duration / len(themes)

    distributed = []
    for i, theme in enumerate(themes):
        distributed.append({
            **theme,
            'start': i * theme_duration,
            'duration': theme_duration,
        })

    return distributed

def create_harmonic_background_filter(themes_timeline, width, height, duration, output_path):
    """
    Create dynamic background that changes based on detected themes
    """

    # Build time-varying filter that adapts to themes
    # For MVP, we'll create segments with smooth transitions

    segments = []

    for i, theme in enumerate(themes_timeline):
        visuals = map_theme_to_visuals(theme['name'], theme['resonance'])

        start = theme['start']
        end = start + theme['duration']

        # Create filter for this theme segment
        base_gradient = (
            f"r='{visuals['base_r']}+45*sin(2*PI*T/18+Y/H*5+X/W*2)':"
            f"g='{visuals['base_g']}+20*sin(2*PI*T/22+Y/H*5)':"
            f"b='{visuals['base_b']}+90*sin(2*PI*T/14+Y/H*5-X/W)'"
        )

        golden_particles = (
            f"r='if(lt(random(0)*255,{visuals['particle_density']}),clip(r(X,Y)+140,0,255),r(X,Y))':"
            f"g='if(lt(random(0)*255,{visuals['particle_density']}),clip(g(X,Y)+100,0,255),g(X,Y))':"
            f"b='if(lt(random(0)*255,{visuals['particle_density']}),clip(b(X,Y)+20,0,255),b(X,Y))'"
        )

        vortex_intensity = visuals['vortex_intensity']
        spiral_vortex = (
            f"r='clip(r(X,Y)+{30*vortex_intensity}*sin(atan2(Y-H/2,X-W/2)*3+hypot(X-W/2,Y-H/2)/80-T*1.5),0,255)':"
            f"g='clip(g(X,Y)+{15*vortex_intensity}*sin(atan2(Y-H/2,X-W/2)*3+hypot(X-W/2,Y-H/2)/100-T*1.2),0,255)':"
            f"b='clip(b(X,Y)+{50*vortex_intensity}*sin(atan2(Y-H/2,X-W/2)*3+hypot(X-W/2,Y-H/2)/60-T*2),0,255)'"
        )

        segments.append({
            'gradient': base_gradient,
            'particles': golden_particles,
            'vortex': spiral_vortex,
        })

    # For MVP, use average of all segments (in future, make it truly dynamic)
    # Average the visual parameters
    avg_segment = segments[len(segments)//2] if segments else segments[0]

    vignette = (
        "r='r(X,Y)*(1-0.5*(1-exp(-0.0000008*hypot(X-W/2,Y-H/2)^2))*(0.7+0.3*sin(2*PI*T/25)))':"
        "g='g(X,Y)*(1-0.6*(1-exp(-0.0000008*hypot(X-W/2,Y-H/2)^2))*(0.7+0.3*sin(2*PI*T/25)))':"
        "b='b(X,Y)*(1-0.4*(1-exp(-0.0000008*hypot(X-W/2,Y-H/2)^2))*(0.7+0.3*sin(2*PI*T/25)))'"
    )

    filter_chain = (
        f"geq={avg_segment['gradient']},"
        f"geq={avg_segment['particles']},"
        f"geq={avg_segment['vortex']},"
        f"geq={vignette},"
        f"gblur=sigma=2.5"
    )

    cmd = [
        'ffmpeg',
        '-f', 'lavfi',
        '-i', f'color=c=black:s={width}x{height}:d={duration},format=rgb24',
        '-vf', filter_chain,
        '-c:v', 'libx264',
        '-preset', 'medium',
        '-crf', '18',
        '-pix_fmt', 'yuv420p',
        '-y',
        output_path
    ]

    return cmd

def create_harmonic_text_overlays(themes_timeline):
    """
    Use expanded harmonic text as overlays
    """
    filters = []

    # Title card
    filters.append(
        "drawtext=text='HARMONIC VIDEO':"
        "fontsize='75+15*sin(2*PI*t/2.5)':"
        "fontcolor=#FFD700@0.98:"
        "x='(w-text_w)/2':"
        "y='(h-text_h)/2-110+8*sin(2*PI*t/1.5)':"
        "enable='between(t,0,4)':"
        "alpha='if(lt(t,0.8),t/0.8,if(gt(t,3.2),(4-t)/0.8,1))':"
        "shadowcolor=#6A11CB@0.8:shadowx=3:shadowy=3"
    )

    # Theme overlays using detected themes
    for theme in themes_timeline:
        start = theme['start']
        end = start + theme['duration']
        fade_duration = 1.0

        # Theme name
        theme_name = theme['name'].replace("'", "\\'")
        filters.append(
            f"drawtext=text='{theme_name}':"
            f"fontsize='68+12*sin(2*PI*t/3)':"
            f"fontcolor=#FFD700@0.98:"
            "x='(w-text_w)/2':"
            "y='70+6*sin(2*PI*t/2)':"
            f"enable='between(t,{start},{end})':"
            f"alpha='if(lt(t,{start+fade_duration}),(t-{start})/{fade_duration},if(gt(t,{end-fade_duration}),({end}-t)/{fade_duration},1))':"
            "shadowcolor=#6A11CB@0.9:shadowx=4:shadowy=4"
        )

        # Theme vibe (core essence)
        theme_vibe = theme['vibe'].replace("'", "\\'")
        filters.append(
            f"drawtext=text='{theme_vibe}':"
            f"fontsize=34:"
            f"fontcolor=#DDA0DD@0.9:"
            "x='(w-text_w)/2':"
            "y=160:"
            f"enable='between(t,{start},{end})':"
            f"alpha='if(lt(t,{start+fade_duration}),(t-{start})/{fade_duration},if(gt(t,{end-fade_duration}),({end}-t)/{fade_duration},1))':"
            "shadowcolor=black@0.7:shadowx=2:shadowy=2"
        )

        # Resonance strength indicator
        resonance_bars = '█' * theme['resonance']
        filters.append(
            f"drawtext=text='{resonance_bars}':"
            f"fontsize=28:"
            f"fontcolor=#FFD700@0.7:"
            "x='(w-text_w)/2':"
            "y=210:"
            f"enable='between(t,{start},{end})':"
            f"alpha='if(lt(t,{start+fade_duration}),(t-{start})/{fade_duration},if(gt(t,{end-fade_duration}),({end}-t)/{fade_duration},1))'"
        )

    # Watermark
    filters.append(
        "drawtext=text='harmonic augmntd diffusion':"
        "fontsize='17+2*sin(2*PI*t/8)':"
        "fontcolor=#DDA0DD@0.5:"
        "x='(w-text_w)/2':"
        "y='h-45'"
    )

    return ','.join(filters)

def get_audio_duration(audio_path):
    """Get duration of audio file"""
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

def generate_harmonic_video(audio_path, output_path, theme='cosmic'):
    """
    Generate video using harmonic analysis to drive visuals
    """

    print("🌌 HARMONIC AUGMNTD DIFFUSION VIDEO GENERATOR")
    print(f"   Audio: {audio_path}")

    # Phase 0: Harmonic Analysis
    themes = run_harmonic_analysis(audio_path)

    if not themes:
        print("⚠️  No harmonic analysis available, using defaults")
        themes = [{
            'name': 'COSMIC RESONANCE',
            'resonance': 3,
            'vibe': 'Pattern emergence from the void',
            'expanded_text': '',
        }]

    # Get duration and distribute themes
    duration = get_audio_duration(audio_path)
    themes_timeline = distribute_themes_over_duration(themes, duration)

    print(f"   Duration: {duration:.2f}s")
    print(f"   Themes distributed: {len(themes_timeline)}")
    for t in themes_timeline:
        print(f"      • {t['name']} (Resonance: {'█'*t['resonance']}) @ {t['start']:.1f}s")

    width, height = 1920, 1080

    # Phase 1: Generate background
    print("⚡ Phase 1: Generating theme-reactive diffusion field...")
    temp_bg = output_path.replace('.mp4', '_harmonic_bg.mp4')

    bg_cmd = create_harmonic_background_filter(themes_timeline, width, height, duration, temp_bg)

    result = subprocess.run(bg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if result.returncode != 0:
        print(f"❌ Background creation error:\n{result.stderr}")
        raise Exception("Background creation failed")

    # Phase 2: Add harmonic text overlays
    print("✨ Phase 2: Crystallizing harmonic text overlays...")
    text_filter = create_harmonic_text_overlays(themes_timeline)

    # Phase 3: Final composition
    print("🔮 Phase 3: Integrative ingression...")
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
        print(f"❌ Final composition error:\n{result.stderr}")
        raise Exception("Video generation failed")

    if not os.path.exists(output_path):
        raise Exception("Video file was not created")

    file_size = os.path.getsize(output_path)
    print(f"✨ HARMONIC video manifested: {output_path}")
    print(f"   Size: {file_size / 1024 / 1024:.2f}MB")
    print("🌌 Themes diffused into visual reality!")

    return output_path

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 video_generator_harmonic.py <audio_path> <output_path> [theme]")
        sys.exit(1)

    audio_path = sys.argv[1]
    output_path = sys.argv[2]
    theme = sys.argv[3] if len(sys.argv) > 3 else 'cosmic'

    if not os.path.exists(audio_path):
        print(f"❌ Audio file not found: {audio_path}")
        sys.exit(1)

    try:
        generate_harmonic_video(audio_path, output_path, theme)
    except Exception as e:
        print(f"❌ Video generation failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
