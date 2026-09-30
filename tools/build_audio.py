"""Record Leo's voice: one MP3 per phrase in tools/phrases.json, plus audio/manifest.js.

Voice: Kokoro-82M (Apache-2.0), American English voice "af_heart", run locally with kokoro-onnx.
Usage:
  pip install kokoro-onnx lameenc numpy
  # model files: https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.0
  node tools/export_phrases.js
  python3 tools/build_audio.py kokoro-v1.0.onnx voices-v1.0.bin [--all] [--redo "phrase" ...]
Existing clips are reused, so re-running only records new phrases (plus any passed with --redo,
or everything with --all). A newly recorded clip is named after its content, so browsers never
play a stale cached copy.
Every clip is brought to the same loudness (LOUDNESS_DB), with a limiter so it never clips.
  python3 tools/build_audio.py --relevel   # re-level the existing clips (needs: pip install av)
"""
import hashlib, json, os, re, sys
import numpy as np
import lameenc

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIO = os.path.join(ROOT, 'audio')
VOICE = 'af_heart'

# How each letter name must sound (checked in the phonemes before a clip is recorded).
LETTER_PHONEMES = {
    'A': 'eɪ', 'B': 'biː', 'C': 'siː', 'D': 'diː', 'E': 'iː', 'F': 'ɛf', 'G': 'dʒiː', 'H': 'eɪtʃ', 'I': 'aɪ', 'J': 'dʒeɪ',
    'K': 'keɪ', 'L': 'ɛl', 'M': 'ɛm', 'N': 'ɛn', 'O': 'oʊ', 'P': 'piː', 'Q': 'kjuː', 'R': 'ɑːɹ', 'S': 'ɛs', 'T': 'tiː',
    'U': 'juː', 'V': 'viː', 'W': 'dʌbəljuː', 'X': 'ɛks', 'Y': 'waɪ', 'Z': 'ziː',
}
# Phrases spoken from different text or phonemes.
OVERRIDES = {
    'a': 'uh.',  # the sight word "a" is said "uh", not the letter name
}
PHONEME_OVERRIDES = {
    'an': 'ˈæn.',  # stressed, so it is not heard as the letter N
}
# Lines that sound better synthesized on their own than cut out of the carrier sentence.
DIRECT = {'A chick!'}
# Short lines are cut out of this sentence, so they start cleanly instead of with a stray sound.
CARRIER = 'The next word is:'
STRESS = str.maketrans('', '', 'ˈˌ')


def is_article(text, m):
    """'A monkey!' starts with the article; 'A is for apple' and 'A, magic e' name the letter."""
    return m.group(1) == 'A' and m.start() == 0 and re.match(r' (?!is\b)[a-z]', text[m.end():]) is not None


def phonemes_for(kokoro, phrase):
    """Phonemes for a phrase, with every letter name checked."""
    if phrase in PHONEME_OVERRIDES:
        return PHONEME_OVERRIDES[phrase]
    if phrase in OVERRIDES:
        return kokoro.tokenizer.phonemize(OVERRIDES[phrase], 'en-us')
    letters = [m.group(1) for m in re.finditer(r'\b([A-Z])\b', phrase) if not is_article(phrase, m)]
    # a lone A between words is read as the article, so it is spoken via the placeholder "hey"
    text = re.sub(r'\b([A-Z])\b', lambda m: m.group(1) if is_article(phrase, m) or m.group(1) != 'A' else 'hey', phrase)
    if not re.search(r'[.!?:]$', text):
        text += '.'  # a lone word sounds complete when it ends like a sentence
    ph = kokoro.tokenizer.phonemize(text, 'en-us')
    ph = re.sub(r'h([ˈˌ]?)eɪ', r'\1eɪ', ph)
    flat = ph.translate(STRESS).replace(' ', '')
    for L in set(letters):
        need = phrase.count(L) if L != 'I' else 1
        if flat.count(LETTER_PHONEMES[L]) < min(need, letters.count(L)):
            raise SystemExit(f'letter {L} not pronounced as its name in {phrase!r}: {ph}')
    return ph


def cut_after_pause(x, rate):
    """Keep the audio after the longest pause (the carrier's colon), or None if there is no clear pause."""
    f = int(rate * 0.01)
    rms = np.array([np.sqrt(np.mean(x[i:i + f] ** 2)) for i in range(0, len(x) - f, f)])
    quiet = list(rms < 0.03 * rms.max()) + [False]
    runs, s = [], None
    for i, q in enumerate(quiet):
        if q and s is None:
            s = i
        if not q and s is not None:
            runs.append((s, i))
            s = None
    runs = [r for r in runs if r[1] < len(rms) - 15]  # at least 150 ms of speech after the pause
    if not runs:
        return None
    s, e = max(runs, key=lambda r: r[1] - r[0])
    return x[max(0, e * f - int(0.03 * rate)):] if e - s >= 8 else None


def synthesize(kokoro, phrase):
    ph = phonemes_for(kokoro, phrase)
    words = len(phrase.split())
    speed = 0.85 if words <= 2 else 0.92  # single words a little slower
    direct, rate = kokoro.create(ph, voice=VOICE, speed=speed, lang='en-us', is_phonemes=True)
    direct = np.asarray(direct, np.float32)
    # lines ending in ':' lead into another clip; the cut is unreliable for them
    if words <= 3 and phrase not in DIRECT and not phrase.endswith(':') and not re.search(r'[,;:.!?]', phrase[:-1]):
        carrier = kokoro.tokenizer.phonemize(CARRIER, 'en-us')
        full, rate = kokoro.create(carrier + ' ' + ph, voice=VOICE, speed=speed, lang='en-us', is_phonemes=True)
        cut = cut_after_pause(np.asarray(full, np.float32), rate)
        if cut is not None and 0.6 * len(direct) <= len(cut) <= 1.8 * len(direct):
            return cut, rate
    return direct, rate


def clip_name(mp3):
    return hashlib.sha1(mp3).hexdigest()[:12] + '.mp3'


def old_manifest():
    path = os.path.join(AUDIO, 'manifest.js')
    if not os.path.exists(path):
        return {}
    return json.loads(open(path, encoding='utf-8').read().split('=', 1)[1].strip().rstrip(';'))


LOUDNESS_DB = -8      # loudness of the spoken parts before limiting (RMS, dBFS); phones play quietly, so this is loud
CEILING = 0.94        # peak limit
MAX_BOOST_DB = 12


def _window_min(g, n):
    """Minimum of g over [i - n, i + n] for every i."""
    pad = np.concatenate([np.full(n, g[0]), g, np.full(n, g[-1])])
    return np.lib.stride_tricks.sliding_window_view(pad, 2 * n + 1).min(axis=1)


def _smooth(g, n):
    """Moving average over [i - n/2, i + n/2]."""
    k = n // 2
    pad = np.concatenate([np.full(k, g[0]), g, np.full(k, g[-1])])
    c = np.concatenate([[0.0], np.cumsum(pad, dtype=np.float64)])
    return ((c[2 * k + 1:] - c[:-2 * k - 1]) / (2 * k + 1)).astype(np.float32)


def level(x, rate):
    """Bring the spoken parts to LOUDNESS_DB, then limit peaks to CEILING (no clipping)."""
    x = np.asarray(x, np.float32)
    f = max(1, int(rate * 0.05))
    rms = np.array([np.sqrt(np.mean(x[i:i + f] ** 2)) for i in range(0, max(1, len(x) - f), f)])
    if not len(rms) or rms.max() == 0:
        return x
    active = rms[rms > 0.1 * rms.max()]
    gain = min(10 ** ((LOUDNESS_DB - 20 * np.log10(np.sqrt(np.mean(active ** 2)))) / 20), 10 ** (MAX_BOOST_DB / 20))
    y = x * gain
    # look-ahead limiter: the smoothed gain never exceeds what each sample needs (min window >= smoothing window)
    need = np.minimum(1.0, CEILING / np.maximum(np.abs(y), 1e-9)).astype(np.float32)
    n = max(1, int(rate * 0.006))
    need = np.minimum(need, _smooth(_window_min(need, n), n))
    return np.clip(y * need, -CEILING, CEILING)


def to_mp3(pcm, rate):
    x = np.asarray(pcm, dtype=np.float32)
    # trim silence at both ends (relative to the peak, so quiet final consonants survive), keep a pad
    peak = np.abs(x).max() or 1.0
    loud = np.where(np.abs(x) > 0.01 * peak)[0]
    if len(loud):
        pad = int(0.07 * rate)
        x = x[max(0, loud[0] - pad): loud[-1] + pad]
    return encode(level(x, rate), rate)


def _lame(x, rate):
    x = np.clip(np.asarray(x, np.float32) * 32767, -32767, 32767).astype(np.int16)
    enc = lameenc.Encoder()
    enc.set_bit_rate(48)
    enc.set_in_sample_rate(rate)
    enc.set_channels(1)
    enc.set_quality(2)
    return enc.encode(x.tobytes()) + enc.flush()


def _decoded_peak(mp3):
    """Peak of the decoded MP3 (the encoder can overshoot), or None without PyAV."""
    try:
        import av, io
        with av.open(io.BytesIO(mp3), format='mp3') as c:
            x = np.concatenate([fr.to_ndarray().astype(np.float32).reshape(-1) for fr in c.decode(audio=0)])
        return float(np.abs(x).max() / (32768 if np.abs(x).max() > 2 else 1))
    except ImportError:
        return None


def encode(x, rate):
    """MP3 that does not clip when played: if the decoded peaks overshoot, turn it down a little."""
    x = np.asarray(x, np.float32)
    for _ in range(4):
        mp3 = _lame(x, rate)
        peak = _decoded_peak(mp3)
        if peak is None or peak <= 0.995:
            break
        x = x * (0.985 / peak)
    return mp3


def decode(path):
    import av
    with av.open(path) as c:
        rate = c.streams.audio[0].rate
        x = np.concatenate([fr.to_ndarray().astype(np.float32).reshape(-1) for fr in c.decode(audio=0)])
    return (x / 32768 if np.abs(x).max() > 2 else x), rate


def write_manifest(manifest):
    # remove clips no longer used (only voice clips, which are named by their hash; music.mp3 stays)
    keep = set(manifest.values())
    for f in os.listdir(AUDIO):
        if re.fullmatch(r'[0-9a-f]{12}\.mp3', f) and f not in keep:
            os.remove(os.path.join(AUDIO, f))
    with open(os.path.join(AUDIO, 'manifest.js'), 'w', encoding='utf-8') as f:
        f.write('// Generated by tools/build_audio.py: phrase -> recorded clip\n')
        f.write('window.PHONICS_CLIPS = ' + json.dumps(manifest, ensure_ascii=False, indent=0) + ';\n')
    import stamp
    stamp.main()


def relevel():
    """Bring the existing clips to the current loudness without recording them again."""
    manifest = {}
    for ph, name in old_manifest().items():
        x, rate = decode(os.path.join(AUDIO, name))
        mp3 = encode(level(x, rate), rate)
        manifest[ph] = clip_name(mp3)
        with open(os.path.join(AUDIO, manifest[ph]), 'wb') as f:
            f.write(mp3)
    write_manifest(manifest)
    print(f'{len(manifest)} clips re-levelled')


def main(model, voices, redo=(), everything=False):
    from kokoro_onnx import Kokoro
    kokoro = Kokoro(model, voices)
    phrases = json.load(open(os.path.join(ROOT, 'tools', 'phrases.json')))
    os.makedirs(AUDIO, exist_ok=True)
    old = {} if everything else old_manifest()
    manifest, made = {}, 0
    for ph in phrases:
        if ph in old and ph not in redo and os.path.exists(os.path.join(AUDIO, old[ph])):
            manifest[ph] = old[ph]
            continue
        pcm, rate = synthesize(kokoro, ph)
        mp3 = to_mp3(pcm, rate)
        manifest[ph] = clip_name(mp3)
        with open(os.path.join(AUDIO, manifest[ph]), 'wb') as f:
            f.write(mp3)
        made += 1
    write_manifest(manifest)
    print(f'{len(phrases)} phrases, {made} new clips')


if __name__ == '__main__':
    args = sys.argv[1:]
    if args == ['--relevel']:
        sys.exit(relevel())
    redo = set(args[args.index('--redo') + 1:]) if '--redo' in args else set()
    args = args[:args.index('--redo')] if '--redo' in args else args
    everything = '--all' in args
    args = [a for a in args if a != '--all']
    if len(args) < 2:
        sys.exit(__doc__)
    main(args[0], args[1], redo, everything)
