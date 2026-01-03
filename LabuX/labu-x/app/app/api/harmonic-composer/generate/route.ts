import { NextRequest, NextResponse } from 'next/server';
import { writeFile, unlink, readFile } from 'fs/promises';
import { join } from 'path';
import { spawn } from 'child_process';
import { randomUUID } from 'crypto';

export const maxDuration = 300; // 5 minutes
export const dynamic = 'force-dynamic';

export async function POST(request: NextRequest) {
  const jobId = randomUUID();
  const tempDir = '/tmp';

  let audioPath: string | null = null;
  let videoPath: string | null = null;

  try {
    // Parse form data
    const formData = await request.formData();
    const file = formData.get('file') as File;
    const theme = formData.get('theme') as string || 'cosmic';

    if (!file) {
      return NextResponse.json({ error: 'No file provided' }, { status: 400 });
    }

    // Save uploaded audio file
    const bytes = await file.arrayBuffer();
    const buffer = Buffer.from(bytes);
    audioPath = join(tempDir, `${jobId}-audio.m4a`);
    await writeFile(audioPath, buffer);

    console.log(`🎙️  Audio saved: ${audioPath} (${(buffer.length / 1024 / 1024).toFixed(2)}MB)`);

    // Generate video using Python script
    videoPath = join(tempDir, `${jobId}-video.mp4`);

    await generateVideo(audioPath, videoPath, theme);

    // Read generated video
    const videoBuffer = await readFile(videoPath);

    // Cleanup temp files
    await Promise.all([
      audioPath ? unlink(audioPath).catch(() => {}) : Promise.resolve(),
      videoPath ? unlink(videoPath).catch(() => {}) : Promise.resolve(),
    ]);

    // Return video as response
    return new NextResponse(videoBuffer, {
      status: 200,
      headers: {
        'Content-Type': 'video/mp4',
        'Content-Disposition': `attachment; filename="harmonic-video-${jobId}.mp4"`,
        'Content-Length': videoBuffer.length.toString(),
      },
    });

  } catch (error: any) {
    console.error('❌ Video generation error:', error);

    // Cleanup on error
    if (audioPath) await unlink(audioPath).catch(() => {});
    if (videoPath) await unlink(videoPath).catch(() => {});

    return NextResponse.json(
      { error: error.message || 'Video generation failed' },
      { status: 500 }
    );
  }
}

function generateVideo(audioPath: string, outputPath: string, theme: string): Promise<void> {
  return new Promise((resolve, reject) => {
    const scriptPath = join(process.cwd(), '..', 'scripts', 'video_generator.py');

    console.log(`🎬 Starting video generation...`);
    console.log(`   Audio: ${audioPath}`);
    console.log(`   Output: ${outputPath}`);
    console.log(`   Theme: ${theme}`);
    console.log(`   Script: ${scriptPath}`);

    const pythonProcess = spawn('python3', [
      scriptPath,
      audioPath,
      outputPath,
      theme,
    ]);

    let stdout = '';
    let stderr = '';

    pythonProcess.stdout.on('data', (data) => {
      const output = data.toString();
      stdout += output;
      console.log(output.trim());
    });

    pythonProcess.stderr.on('data', (data) => {
      const output = data.toString();
      stderr += output;
      console.error(output.trim());
    });

    pythonProcess.on('close', (code) => {
      if (code === 0) {
        console.log('✅ Video generation complete');
        resolve();
      } else {
        console.error(`❌ Video generation failed with code ${code}`);
        reject(new Error(`Video generation failed: ${stderr || 'Unknown error'}`));
      }
    });

    pythonProcess.on('error', (error) => {
      console.error('❌ Failed to start Python process:', error);
      reject(error);
    });
  });
}
