#!/usr/bin/env python3
"""Select contextual replacements for the original 1,000-word draft bank."""
import argparse
import collections
import csv
import json
import re
import sqlite3
from pathlib import Path
from conversation_growth import FUNCTION_EXAMPLES

ROOT=Path(__file__).resolve().parent
TOKEN=re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)*",re.UNICODE)
BAD=re.compile(r'\b(kill|murder|shot|gun|rape|fuck|bitch|shit|suicide|torture|corpse)\w*\b',re.I)

def main(source_dir):
    c=sqlite3.connect(ROOT/'french_course.sqlite');c.row_factory=sqlite3.Row
    ref=json.loads((ROOT/'completion_reference.json').read_text())
    words=[dict(r) for r in c.execute('SELECT * FROM conversation_words WHERE rank<=1000 ORDER BY rank')]
    targets=collections.defaultdict(set)
    for r in words:
        w=r['french'];forms={w.casefold()}
        if w in ref['verbs'] and ref['lexical'][w]['primary_pos']=='verb':
            forms.update(form[0].casefold() for cell in ref['verbs'][w]['finite'] if cell[:2]==['indicative','present'] for form in cell[3])
        for f in forms:targets[f].add(w)
    corpus=collections.defaultdict(list)
    for line in (source_dir/'examples.tsv').read_text().splitlines():
        p=line.split('\t')
        if len(p)<2:continue
        en,fr=p[:2]
        if len(en)>110 or len(fr)>120 or BAD.search(en):continue
        if not 4<=len(TOKEN.findall(fr))<=14:continue
        hits=set()
        for token in TOKEN.findall(fr):hits.update(targets.get(token.casefold(),()))
        for w in hits:corpus[w].append((fr,en))
    with (ROOT/'authored_usage.tsv').open(encoding='utf-8') as f:
        authored={r['french']:r for r in csv.DictReader(f,delimiter='\t')}
    output=[];missing=[]
    for r in words:
        w=r['french'];pos=ref['lexical'][w]['primary_pos']
        if w in authored:
            entry=authored[w]
            output.append([w,entry['example_fr'],entry['example_en'],'authored_unreviewed','Original project teaching example']);continue
        if w in FUNCTION_EXAMPLES and w!='devoir':
            fr,en=FUNCTION_EXAMPLES[w]
            output.append([w,fr,en,'authored_unreviewed','Original project teaching example']);continue
        gloss=re.sub(r'\([^)]*\)','',r['meaning_en'].lower()).removeprefix('to ')
        senses=[s.strip() for s in re.split(r'[;/]',gloss) if len(s.strip())>=3]
        best=None
        for fr,en in corpus[w]:
            hits=sum(bool(re.search(r'\b'+re.escape(s)+r'\b',en.lower())) for s in senses)
            if not hits:continue
            n=len(TOKEN.findall(fr));score=hits*20-abs(n-8)
            if re.search(r'\b(Tom|Mary|Boston)\b',fr):score-=5
            if re.search(r'\b(fut|furent|eut|fit|vint|prit)\b',fr):score-=6
            if best is None or score>best[0]:best=(score,fr,en)
        if best:
            output.append([w,best[1],best[2],'corpus_unreviewed','Tatoeba via desmondyeoh/data-eng-fra'])
        else:missing.append([w,pos,r['meaning_en']])
    with (ROOT/'completion_usage.tsv').open('w',encoding='utf-8',newline='') as f:
        writer=csv.writer(f,delimiter='\t');writer.writerow(['french','example_fr','example_en','example_status','example_source']);writer.writerows(output)
    (source_dir/'missing_examples.json').write_text(json.dumps(missing,ensure_ascii=False,indent=2))
    print('Prepared',len(output),'examples; author',len(missing),'remaining examples in',source_dir/'missing_examples.json')
    print(json.dumps(missing,ensure_ascii=False))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source-dir',type=Path,required=True);main(p.parse_args().source_dir)
