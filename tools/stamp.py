"""Write the current versions of audio/manifest.js and audio/music.mp3 into index.html.

The page loads `audio/manifest.js?v=<version>` and `audio/music.mp3?v=<version>`, so a browser can
never combine a new page with an older, cached clip list (whose clips may no longer exist).
Run after changing the clips or the music (tools/build_audio.py and tools/make_music.py call it).
"""
import hashlib, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def version(path):
    with open(os.path.join(ROOT, path), 'rb') as f:
        return hashlib.sha1(f.read()).hexdigest()[:10]


def main():
    page = os.path.join(ROOT, 'index.html')
    html = open(page, encoding='utf-8').read()
    new = re.sub(r"var AUDIO_VERSION = \{manifest:'[^']*', music:'[^']*'\};",
                 f"var AUDIO_VERSION = {{manifest:'{version('audio/manifest.js')}', music:'{version('audio/music.mp3')}'}};", html)
    if new != html:
        open(page, 'w', encoding='utf-8').write(new)
    print('index.html audio versions:', re.search(r'var AUDIO_VERSION = [^;]*;', new).group(0))


if __name__ == '__main__':
    main()
