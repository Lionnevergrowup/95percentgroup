"""Render the background music loop: audio/music.mp3.

An original, cheerful tune in C major (100 BPM, 16 bars, about 38 s) played by a
marimba, ukulele-style plucked chords, a soft plucked bass and a quiet shaker.
Everything is synthesized here, so the music has no licence restrictions.
The last bar ends on a rest, so the loop joins without a bump.

Usage: pip install numpy lameenc; python3 tools/make_music.py
"""
import os
import numpy as np
import lameenc

RATE = 32000
BPM = 100
BEAT = 60 / BPM
BAR = 4 * BEAT
BARS = 16
rng = np.random.default_rng(7)

# chords per bar (a bar with two chords lists both; the second starts on beat 3)
CHORDS = {'C': [60, 64, 67], 'G': [59, 62, 67], 'Am': [57, 60, 64], 'F': [57, 60, 65], 'Em': [59, 64, 67]}
ROOT = {'C': 48, 'G': 43, 'Am': 45, 'F': 41, 'Em': 40}
FIFTH = {'C': 43, 'G': 50, 'Am': 52, 'F': 48, 'Em': 47}
PROGRESSION = ['C', 'G', 'Am', 'F', 'C', 'G', ('F', 'G'), 'C',
               'F', 'C', 'G', 'Am', 'F', 'C', 'G', 'C']

# melody: (bar, beat, length in beats, midi note)
E5, G5, C6, D6, B4, D5, F5, A5, B5, C5 = 76, 79, 84, 86, 71, 74, 77, 81, 83, 72
MELODY_BARS = [
    [(0, 1, E5), (1, 1, G5), (2, 1.5, C6), (3.5, .5, G5)],
    [(0, 1, B4), (1, 1, D5), (2, 1.5, G5), (3.5, .5, F5)],
    [(0, 1, E5), (1, .5, C5), (1.5, .5, E5), (2, 1.5, A5), (3.5, .5, G5)],
    [(0, 1, F5), (1, 1, A5), (2, 1, G5), (3, 1, E5)],
    [(0, .5, E5), (.5, .5, E5), (1, 1, G5), (2, 1, C6), (3, .5, D6), (3.5, .5, C6)],
    [(0, 1, B5), (1, 1, G5), (2, 1.5, D5), (3.5, .5, G5)],
    [(0, 1, A5), (1, 1, F5), (2, 1, G5), (3, 1, B5)],
    [(0, 2, C6), (2, 1, G5), (3, 1, E5)],
    [(0, .5, A5), (.5, .5, G5), (1, 1, F5), (2, 1, A5), (3, 1, C6)],
    [(0, 1, G5), (1, 1, E5), (2, 1, C5), (3, 1, E5)],
    [(0, .5, D5), (.5, .5, E5), (1, 1, F5), (2, 1, G5), (3, 1, B5)],
    [(0, 1.5, C6), (1.5, .5, B5), (2, 1, A5), (3, 1, E5)],
    [(0, 1, F5), (1, 1, A5), (2, 1, C6), (3, 1, A5)],
    [(0, 1, G5), (1, .5, E5), (1.5, .5, G5), (2, 2, C6)],
    [(0, 1, D6), (1, 1, B5), (2, 1, G5), (3, 1, F5)],
    [(0, 1, E5), (1, 1, D5), (2, 1, C5)],          # beat 4 rests, so the loop can restart
]

hz = lambda m: 440.0 * 2 ** ((m - 69) / 12)


def marimba(f, dur):
    t = np.arange(int((dur + 0.9) * RATE)) / RATE
    attack = 1 - np.exp(-t * 400)
    tone = (np.sin(2 * np.pi * f * t) * np.exp(-t * 4.5)
            + 0.30 * np.sin(2 * np.pi * 3.93 * f * t) * np.exp(-t * 18)
            + 0.07 * np.sin(2 * np.pi * 9.2 * f * t) * np.exp(-t * 45))
    return tone * attack


def pluck(f, dur, bright=0.5, decay=0.996):
    """Karplus-Strong string (ukulele / bass)."""
    n = int((dur + 0.6) * RATE)
    period = max(2, int(RATE / f))
    buf = rng.uniform(-1, 1, period)
    buf = np.convolve(buf, [bright, 1 - bright], mode='same')  # soften the first burst
    out = np.empty(n)
    for i in range(n):
        out[i] = buf[i % period]
        buf[i % period] = decay * 0.5 * (buf[i % period] + buf[(i + 1) % period])
    return out * (1 - np.exp(-np.arange(n) / RATE * 300))


def shaker(dur=0.07):
    t = np.arange(int(dur * RATE)) / RATE
    noise = rng.uniform(-1, 1, len(t))
    noise = np.diff(np.concatenate([[0], noise]))           # high-pass: keep the hiss
    return noise * np.exp(-t * 55) * (1 - np.exp(-t * 900))


def add(track, at, sound, gain):
    i = int(at * RATE)
    j = min(len(track), i + len(sound))
    track[i:j] += gain * sound[:j - i]


def render():
    total = int((BARS * BAR + 2.0) * RATE)     # 2 s of room for the reverb tail
    mel, chords, bass, perc = (np.zeros(total) for _ in range(4))
    for b, prog in enumerate(PROGRESSION):
        start = b * BAR
        halves = prog if isinstance(prog, tuple) else (prog, prog)
        for half, name in enumerate(halves):
            beat0 = half * 2
            # ukulele strums on beats 2 and 4 (off-beat feel), gently staggered
            for beat in (beat0 + 1,):
                if b == BARS - 1 and beat >= 3:
                    continue
                for k, m in enumerate(CHORDS[name]):
                    add(chords, start + beat * BEAT + k * 0.018, pluck(hz(m), BEAT * 1.2, bright=0.35, decay=0.994), 0.55)
            # bass: root, then fifth
            if not (b == BARS - 1 and half == 1):
                add(bass, start + beat0 * BEAT, pluck(hz(ROOT[name]), BEAT * 1.6, bright=0.2, decay=0.998), 0.9)
            if half == 0 and not isinstance(prog, tuple) and b != BARS - 1:
                add(bass, start + 2 * BEAT, pluck(hz(FIFTH[name]), BEAT * 1.4, bright=0.2, decay=0.998), 0.7)
        # shaker on every eighth note, off-beats a little louder
        for e in range(8):
            if b == BARS - 1 and e >= 6:
                continue
            add(perc, start + e * BEAT / 2, shaker(), 0.10 if e % 2 else 0.05)
        for beat, length, note in MELODY_BARS[b]:
            add(mel, start + beat * BEAT, marimba(hz(note), length * BEAT), 0.55 * (0.92 + 0.16 * rng.random()))
    dry = mel + 0.42 * chords + 0.55 * bass + perc
    # small room reverb (convolution with a decaying noise burst)
    t = np.arange(int(1.3 * RATE)) / RATE
    ir = rng.uniform(-1, 1, len(t)) * np.exp(-t * 4.0)
    ir = np.convolve(ir, np.ones(6) / 6, mode='same')   # darker tail
    ir /= np.sqrt(np.sum(ir ** 2))
    n = len(dry) + len(ir)
    wet = np.fft.irfft(np.fft.rfft(dry, n) * np.fft.rfft(ir, n), n)[:len(dry)]
    mix = dry + 0.16 * wet
    # fold the tail back onto the start so the loop is seamless, then cut to exactly 16 bars
    loop_len = int(BARS * BAR * RATE)
    loop = mix[:loop_len].copy()
    tail = mix[loop_len:]
    loop[:len(tail)] += tail
    loop = np.tanh(loop / np.abs(loop).max() * 1.2) / np.tanh(1.2)   # gentle limiter
    return (loop * 0.9 * 32767).astype(np.int16)


def main():
    pcm = render()
    enc = lameenc.Encoder()
    enc.set_bit_rate(64)
    enc.set_in_sample_rate(RATE)
    enc.set_channels(1)
    enc.set_quality(2)
    mp3 = enc.encode(pcm.tobytes()) + enc.flush()
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'audio', 'music.mp3')
    with open(out, 'wb') as f:
        f.write(mp3)
    print(f'{out}: {len(pcm) / RATE:.1f} s, {len(mp3) // 1024} KB')
    import stamp
    stamp.main()


if __name__ == '__main__':
    main()
