# 🦁 Phonics Fun · 幼儿园自然拼读小游戏

An interactive phonics game for kindergarteners, built from the **Kindergarten Phonics Practice: 25-Lesson Home Practice Book**.
It covers the same 25 lessons: letter sounds, short vowels, review lessons, and silent-e (magic e).

根据《Kindergarten Phonics Practice 25-Lesson Home Practice Book》制作的互动网页游戏，适合幼儿园孩子在平板、手机或电脑上玩。

**▶ Play:** https://lionnevergrowup.github.io/95percentgroup/

## What's inside · 内容

Each lesson has 7 short activities that follow the workbook page:

| Activity 活动 | Workbook section 对应练习册 | What the child does 孩子做什么 |
|---|---|---|
| 🔤 Sounds | 1. Say the sounds | Tap the letter cards to hear them, then pop the balloon with the sound Leo says · 听字母发音，戳气球找字母 |
| ✏️ Trace | Write each sound | Trace the letter (or the silent-e word) with a finger · 用手指描写字母 |
| 📖 Read Words / ✨ Magic e | 2. Read the words | Sound out each word, then pick the word you hear; in silent-e lessons, add the magic e (cap → cape) · 拼读单词、对比长短元音 |
| 👀 Sight Words | High-frequency words | Tap the sight words, then pop the bubble with the word you hear · 高频词 |
| 🧩 Spell It | 3. Write the words + 5. Dictation | Hear a word and tap the letters in order · 听音拼词 |
| 💬 Sentence | 4. Read a sentence | Read along, then put the words back in order · 跟读句子、排列句子 |
| 🎨 Draw | 6. Draw and label | Draw a picture and label it with a lesson word; the picture can be saved · 画画并选单词标注 |

- A friendly lion (Leo) speaks every instruction out loud, so children don't need to read directions yet. Tap Leo to hear it again.
- Leo's voice is pre-recorded (`audio/`, 600+ short MP3 clips), so it works in any browser: WeChat, Android phones without an English speech engine, and iPhones with the silent switch on. 语音是预先录好的，微信里、没有英文语音引擎的安卓手机、iPhone 静音模式下都能听到。
- Children earn a ⭐ for each activity and an animal sticker 🏆 for each finished lesson.
- **Parents page (👪)**: the Quick Parent Guide, voice speed, sound effects on/off, a sound test with tips if nothing plays, a "Refresh to latest version" button, and a "Parent/teacher check" table (sounds, words, writing, sentence) for all 25 lessons.
- Progress is saved in this browser on this device (localStorage). Nothing is sent anywhere.

## Tips · 使用提示

- Turn the volume up. 请把音量调大。If there is still no sound, open the page in a normal browser (in WeChat: tap "…" → "Open in browser") and check that no Bluetooth speaker or headphones are connected.
- Practice 10–15 minutes at a time. 每次练习 10–15 分钟。
- You can add the page to your home screen (Share → Add to Home Screen) so it opens like an app.
- After an update, tap 🔄 (top right of the home screen) to force the newest version to load. 更新后点主页右上角的 🔄 强制刷新。

## Deploy with GitHub Pages · 部署

This is a static site: `index.html`, plus the `fonts/` and `audio/` folders. There is no build step.

1. Open the repository on GitHub → **Settings** → **Pages**.
2. Under **Build and deployment**, set **Source** to **Deploy from a branch**.
3. Pick the **main** branch and the **/ (root)** folder, then click **Save**.
4. After about a minute the game is live at `https://lionnevergrowup.github.io/95percentgroup/`.

To run it locally, open `index.html` in a browser, or run `python3 -m http.server` in this folder and visit http://localhost:8000.

## Changing what Leo says · 修改语音

Every spoken line is listed by `allPhrases()` in `index.html` (fixed lines are in `T`, lines built from lesson data in `P`).
After changing lessons, sentences or phrases, record the new clips:

```sh
pip install piper-tts lameenc numpy
node tools/export_phrases.js            # writes tools/phrases.json (needs the playwright package)
python3 tools/build_audio.py en_US-ljspeech-high.onnx   # records new clips, updates audio/manifest.js
```

The voice model is `en_US-ljspeech-high` from [Piper voices](https://huggingface.co/rhasspy/piper-voices). Any line without a clip falls back to the browser's built-in speech.

## Credits

- Voice: recorded with [Piper](https://github.com/rhasspy/piper) using the LJSpeech voice (trained on the public-domain [LJ Speech dataset](https://keithito.com/LJ-Speech-Dataset/)).
- Fonts: [Andika](https://software.sil.org/andika/) (SIL, designed for beginning readers) and [Fredoka](https://github.com/hafontia/Fredoka-One), both under the SIL Open Font License (see `fonts/OFL-*.txt`).
- Lesson content follows the "Kindergarten Phonics Practice" home practice book, which is original supplemental practice aligned to the Grade K lesson progression. It does not reproduce the commercial Student Workbook.
