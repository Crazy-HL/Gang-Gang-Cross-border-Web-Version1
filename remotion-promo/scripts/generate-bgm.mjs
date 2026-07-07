import {writeFileSync} from 'node:fs';

const sampleRate = 44100;
const duration = 28;
const channels = 2;
const totalSamples = sampleRate * duration;
const dataSize = totalSamples * channels * 2;
const buffer = Buffer.alloc(44 + dataSize);

const writeString = (offset, value) => buffer.write(value, offset, value.length, 'ascii');

writeString(0, 'RIFF');
buffer.writeUInt32LE(36 + dataSize, 4);
writeString(8, 'WAVE');
writeString(12, 'fmt ');
buffer.writeUInt32LE(16, 16);
buffer.writeUInt16LE(1, 20);
buffer.writeUInt16LE(channels, 22);
buffer.writeUInt32LE(sampleRate, 24);
buffer.writeUInt32LE(sampleRate * channels * 2, 28);
buffer.writeUInt16LE(channels * 2, 32);
buffer.writeUInt16LE(16, 34);
writeString(36, 'data');
buffer.writeUInt32LE(dataSize, 40);

const notes = [261.63, 329.63, 392.0, 493.88, 440.0, 392.0, 329.63, 293.66];
const bass = [65.41, 82.41, 98.0, 73.42];

const envelope = (t) => {
  const fadeIn = Math.min(1, t / 1.6);
  const fadeOut = Math.min(1, (duration - t) / 2.4);
  return Math.max(0, Math.min(fadeIn, fadeOut));
};

for (let i = 0; i < totalSamples; i++) {
  const t = i / sampleRate;
  const beat = Math.floor(t * 2);
  const chordIndex = Math.floor(t / 3.5) % notes.length;
  const lead = notes[chordIndex];
  const bassNote = bass[Math.floor(t / 7) % bass.length];
  const pulse = Math.exp(-((t * 2) % 1) * 4.2);
  const shimmer = Math.sin(2 * Math.PI * lead * t) * 0.055;
  const harmony = Math.sin(2 * Math.PI * lead * 1.5 * t) * 0.025;
  const low = Math.sin(2 * Math.PI * bassNote * t) * 0.04 * (0.35 + pulse * 0.65);
  const tick = beat % 4 === 0 ? Math.sin(2 * Math.PI * 900 * t) * pulse * 0.014 : 0;
  const value = (shimmer + harmony + low + tick) * envelope(t);
  const left = Math.max(-1, Math.min(1, value * 0.82));
  const right = Math.max(-1, Math.min(1, value * 0.72 + Math.sin(2 * Math.PI * lead * 0.75 * t) * 0.018 * envelope(t)));
  const offset = 44 + i * channels * 2;
  buffer.writeInt16LE(Math.round(left * 32767), offset);
  buffer.writeInt16LE(Math.round(right * 32767), offset + 2);
}

writeFileSync(new URL('../public/audio/story-bgm.wav', import.meta.url), buffer);
