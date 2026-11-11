#!/usr/bin/env python3
"""Generate a small, reproducible French neural audio bank for static hosting."""
import hashlib
import json
import sqlite3
import subprocess
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
MODEL = 'hexgrad/Kokoro-82M'
REVISION = 'f3ff3571791e39611d31c381e3a41a3af07b4987'
VOICE = 'ff_siwis'


def normalize(text):
    return ' '.join(unicodedata.normalize('NFC', text).replace('’', "'").replace('ʼ', "'").split())


def targets(db):
    queries = (
        'SELECT example_fr FROM pronunciation_items WHERE lesson_id<=14 ORDER BY lesson_id,position',
        'SELECT example_fr FROM lessons WHERE day_number<=14 AND example_fr IS NOT NULL ORDER BY day_number',
        'SELECT front FROM flashcards WHERE lesson_id<=14 AND direction=\'fr_en\' ORDER BY id',
        'SELECT french FROM conversation_words ORDER BY rank LIMIT 100',
        "SELECT french FROM lexemes WHERE french IN ('bonjour','merci','salut','au revoir','s’il vous plaît','oui','non','pardon','excusez-moi')",
    )
    return sorted({normalize(text) for query in queries for (text,) in db.execute(query) if text.strip() and '/' not in text})


def main():
    import numpy as np
    import torch
    from huggingface_hub import hf_hub_download
    from imageio_ffmpeg import get_ffmpeg_exe
    from kokoro import KModel, KPipeline

    torch.set_num_threads(2)
    def download(filename):
        return hf_hub_download(MODEL, filename, revision=REVISION)

    with sqlite3.connect(HERE.parent/'french_course/french_course.sqlite') as db:
        phrases = targets(db)
    out = HERE/'audio'
    out.mkdir(exist_ok=True)
    clips = {}
    model = KModel(repo_id=MODEL, config=download('config.json'), model=download('kokoro-v1_0.pth')).eval()
    voice = torch.load(download(f'voices/{VOICE}.pt'), map_location='cpu', weights_only=True)
    pipeline = KPipeline(lang_code='f', repo_id=MODEL, model=model, device='cpu')
    ffmpeg = get_ffmpeg_exe()
    for text in phrases:
        filename = hashlib.sha256(f'{REVISION}\n{VOICE}\n{text}'.encode()).hexdigest()[:24]+'.mp3'
        file = out/filename
        if not file.is_file():
            with torch.inference_mode():
                chunks = [r.audio.detach().cpu().numpy() for r in pipeline(text, voice=voice) if r.audio is not None]
            if not chunks:
                raise ValueError(f'No speech generated for {text!r}')
            audio = np.concatenate(chunks).astype('<f4')
            if len(audio) < 2400 or not np.isfinite(audio).all() or float(np.abs(audio).max()) < 0.001:
                raise ValueError(f'Invalid speech generated for {text!r}')
            tmp = file.with_suffix('.tmp')
            subprocess.run([ffmpeg,'-v','error','-y','-f','f32le','-ar','24000','-ac','1','-i','pipe:0','-codec:a','libmp3lame','-b:a','48k','-f','mp3',str(tmp)],input=audio.tobytes(),check=True,timeout=30)
            tmp.replace(file)
        clips[text] = filename
    (out/'index.json').write_text(json.dumps({'locale':'fr-FR','model':MODEL,'revision':REVISION,'voice':VOICE,'clips':clips},ensure_ascii=False)+'\n',encoding='utf-8')
    print(f'Generated index for {len(clips)} French neural clips')


if __name__=='__main__':
    main()
