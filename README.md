# 🦁 Phonics Fun

An interactive phonics game for kindergarteners, built from the **Kindergarten Phonics Practice: 25-Lesson Home Practice Book**.
It covers the same 25 lessons: letter sounds, short vowels, review lessons, and silent-e (magic e). It works on tablets, phones and computers.

**▶ Play:** https://lionnevergrowup.github.io/95percentgroup/

Start screen: https://lionnevergrowup.github.io/95percentgroup/#/start · Parents page: https://lionnevergrowup.github.io/95percentgroup/#/parents

## What's inside

Each lesson has 7 short activities that follow the workbook page:

| Activity | Workbook section | What the child does |
|---|---|---|
| 🔤 Sounds | 1. Say the sounds | Tap the letter cards to hear them, then pop the balloon with the sound Leo says |
| ✏️ Trace | Write each sound | Trace the letter (or the silent-e word) with a finger |
| 📖 Read Words / ✨ Magic e | 2. Read the words | Sound out each word, then pick the word you hear; in silent-e lessons, add the magic e (cap → cape) |
| 👀 Sight Words | High-frequency words | Tap the sight words, then pop the bubble with the word you hear |
| 🧩 Spell It | 3. Write the words + 5. Dictation | Hear a word and tap the letters in order |
| 💬 Sentence | 4. Read a sentence | Read along, then put the words back in order |
| 🎨 Draw | 6. Draw and label | Draw a picture and label it with a lesson word; the picture can be saved |

- A friendly lion (Leo) speaks every instruction out loud, so children don't need to read directions yet. Tap Leo to hear it again, or drag him anywhere on the screen (he remembers where; "Put Leo back" in Settings returns him to the corner).
- Cheerful background music plays quietly and dips whenever Leo talks. Turn it off with "🎵 Music" at the bottom of the home screen or in Settings.
- Leo's voice is pre-recorded (`audio/`, 600+ short MP3 clips), so it works in any browser: in-app browsers such as WeChat, Android phones without an English speech engine, and iPhones with the silent switch on.
- Children earn a ⭐ for each activity and an animal sticker 🏆 for each finished lesson.
- **Parents page (👪)**: the Quick Parent Guide, voice speed, sound effects on/off, a sound test with tips if nothing plays, a "Refresh to latest version" button, a "Parent/teacher check" table (sounds, words, writing, sentence) for all 25 lessons that ticks itself as the child plays and can be ticked by hand, and a "Reset progress" button (with a grown-up check).
- Progress is saved in this browser on this device (localStorage). Nothing is sent anywhere.

## Tips

- Turn the volume up. If there is still no sound, open the page in the phone's normal browser (in WeChat: tap "…" → "Open in browser") and check that no Bluetooth speaker or headphones are connected.
- Practice 10–15 minutes at a time.
- You can add the page to your home screen (Share → Add to Home Screen) so it opens like an app.
- After an update, tap 🔄 (top right of the home screen) to force the newest version to load.

## Deploy with GitHub Pages

This is a static site: `index.html`, plus the `fonts/` and `audio/` folders. There is no build step.

1. Open the repository on GitHub → **Settings** → **Pages**.
2. Under **Build and deployment**, set **Source** to **Deploy from a branch**.
3. Pick the **main** branch and the **/ (root)** folder, then click **Save**.
4. After about a minute the game is live at `https://lionnevergrowup.github.io/95percentgroup/`.

To run it locally, run `python3 -m http.server` in this folder and visit http://localhost:8000.

## Changing what Leo says

Every spoken line is listed by `allPhrases()` in `index.html` (fixed lines are in `T`, lines built from lesson data in `P`).
After changing lessons, sentences or phrases, record the new clips:

```sh
pip install kokoro-onnx lameenc numpy
node tools/export_phrases.js     # writes tools/phrases.json (needs the playwright package)
python3 tools/build_audio.py kokoro-v1.0.onnx voices-v1.0.bin   # records new clips, updates audio/manifest.js
```

The model files come from the [kokoro-onnx releases](https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.0). To re-record specific lines, add `--redo "phrase one" "phrase two"`; `--all` re-records everything. Any line without a clip falls back to the browser's built-in speech.

## Background music

`audio/music.mp3` is an original loop (marimba, ukulele-style chords, bass and shaker, about 38 s) synthesized by `tools/make_music.py`, so it has no licence restrictions. Re-create it with `python3 tools/make_music.py`.

## Credits

- Voice: recorded with [Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M) (Apache-2.0), American English voice `af_heart`.
- Fonts: [Andika](https://software.sil.org/andika/) (SIL, designed for beginning readers) and [Fredoka](https://github.com/hafontia/Fredoka-One), both under the SIL Open Font License (see `fonts/OFL-*.txt`).
- Lesson content follows the "Kindergarten Phonics Practice" home practice book, which is original supplemental practice aligned to the Grade K lesson progression. It does not reproduce the commercial Student Workbook.
