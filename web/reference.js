export const referenceLabels = {verbs:'Verb Conjugation',dictionary:'Dictionary'};
const sample = {verbs:['être','avoir','aller','faire','se lever','manger'],dictionary:['bonjour','merci','cheval','heureux','maison','travail']};
const moods = {indicative:'Indicative',conditional:'Conditional',subjunctive:'Subjunctive',imperative:'Imperative'};
const tenseLabels = {present:'Présent',imperfect:'Imparfait',passe_compose:'Passé composé',pluperfect:'Plus-que-parfait',future:'Futur simple',future_perfect:'Futur antérieur',simple_past:'Passé simple',past_anterior:'Passé antérieur',past:'Passé'};
const tenses = ['present','passe_compose','imperfect','pluperfect','future','future_perfect','simple_past','past_anterior','past'];
const persons = ['je','tu','il','il/elle/on','nous','vous','ils/elles'];
const genderNames = {m:'masculine',f:'feminine'};
const featureNames = {m:'masculine',f:'feminine',s:'singular',p:'plural',ms:'masculine singular',mp:'masculine plural',fs:'feminine singular',fp:'feminine plural',Km:'masculine · comparative',Kms:'masculine singular · comparative',Kmp:'masculine plural · comparative',Kfs:'feminine singular · comparative',Kfp:'feminine plural · comparative',none:'invariable'};
const pageSize = 18;
const compareFr = new Intl.Collator('fr');

export function normalizeLookup(s) {
  return String(s ?? '').normalize('NFD').replace(/\p{M}/gu,'').toLowerCase()
    .replace(/œ/g,'oe').replace(/æ/g,'ae').replace(/[’ʼ‘]/g,"'").replace(/\s+/g,' ').trim();
}

export function prepareLookup([key,word,meaning,ipa,shard,tag,forms]) {
  const name=normalizeLookup(word), gloss=normalizeLookup(meaning);
  return {key,word,meaning,ipa,shard,tag,name,gloss,tokens:gloss.split(/[^a-z]+/),forms:new Set(forms.map(normalizeLookup))};
}

export function searchReference(entries, query, kind) {
  const q=normalizeLookup(query);
  if(!q) return sample[kind].map(word=>entries.find(entry=>entry.word===word)).filter(Boolean);
  const exact=String(query).normalize('NFC').trim().toLowerCase();
  const en=q.replace(/^to /,'');
  const scored=[];
  for(const entry of entries){
    let rank=Infinity;
    if(entry.word.toLowerCase()===exact) rank=0;
    else if(entry.name===q) rank=1;
    else if(entry.forms.has(q)) rank=2;
    else if(entry.name.startsWith(q)) rank=3;
    else if(entry.gloss===en || entry.tokens.includes(en)) rank=4;
    else if(entry.name.includes(q)) rank=5;
    else if(en && (entry.gloss.includes(en)||entry.tokens.some(token=>token.startsWith(en)))) rank=6;
    else if(q.length>=2 && [...entry.forms].some(form=>form.startsWith(q))) rank=7;
    if(rank!==Infinity) scored.push({entry,rank});
  }
  return scored.sort((a,b)=>a.rank-b.rank||compareFr.compare(a.entry.word,b.entry.word)).map(x=>x.entry);
}

function byTense(rows) {
  const grouped=new Map();
  for(const row of rows){
    const f=Array.isArray(row)?{mood:row[0],tense:row[1],person:row[2],form:row[3],ipa:row[4],parts:row[6]}:row;
    const group=`${f.mood}/${f.tense}`;
    if(!grouped.has(group))grouped.set(group,[]);
    grouped.get(group).push(f);
  }
  return [...grouped.values()].sort((a,b)=>Object.keys(moods).indexOf(a[0].mood)-Object.keys(moods).indexOf(b[0].mood)||tenses.indexOf(a[0].tense)-tenses.indexOf(b[0].tense));
}

export function createReferenceView(e, listen, icon) {
  const sessions=Object.fromEntries(Object.keys(referenceLabels).map(k=>[k,{query:'',limit:pageSize,selected:'',entries:null,error:false,detailRequest:0}]));
  const shards=new Map();
  const root=kind=>document.querySelector(`[data-reference-view="${kind}"]`);
  const pane=kind=>root(kind)?.querySelector('[data-ref-detail]');

  async function read(path) {
    const response=await fetch(`./data/reference/${path}.json`);
    if(!response.ok)throw Error('Reference data unavailable');
    return response.json();
  }

  function screen(kind) {
    const label=referenceLabels[kind], verb=kind==='verbs';
    return `<section class="reference-page" data-reference-view="${kind}"><div class="page-title-row"><div><div class="eyebrow">French reference</div><h1>${label}</h1><p>${verb?'Find a verb and see how it changes across moods and tenses.':'Look up a word, hear it, and see how to use it in a sentence.'}</p></div></div><div class="reference-grid"><section class="card reference-search"><form data-ref-search="${kind}" role="search" aria-label="Search ${label}"><label for="ref-query">${verb?'Find a verb':'Find a word'}</label><div class="reference-input">${icon('search')}<input id="ref-query" type="search" maxlength="120" autocomplete="off" spellcheck="false" placeholder="${verb?'Try être, suis, or to eat':'Try cheval, chevaux, or horse'}" value="${e(sessions[kind].query)}"></div></form><p class="reference-count" role="status" data-ref-count></p><div data-ref-results></div></section><section class="card reference-detail" id="ref-detail" aria-label="${verb?'Verb details':'Word details'}" data-ref-detail></section></div></section>`;
  }

  function updateResults(kind) {
    const section=root(kind), s=sessions[kind];
    if(!section)return;
    const results=section.querySelector('[data-ref-results]'), count=section.querySelector('[data-ref-count]');
    if(!s.entries){
      count.textContent=s.error?'Could not load the reference.':'Loading search…';
      results.innerHTML=s.error?'<button class="secondary-button" data-action="ref-retry">Try again</button>':'';
      return;
    }
    const hits=searchReference(s.entries,s.query,kind), querying=!!normalizeLookup(s.query);
    count.textContent=querying?`${hits.length.toLocaleString()} ${hits.length===1?'match':'matches'}`:`Try a popular ${kind==='verbs'?'verb':'word'} · ${s.entries.length.toLocaleString()} available`;
    results.innerHTML=hits.length?`<ul class="reference-results">${hits.slice(0,s.limit).map(item=>`<li><button type="button" class="reference-result" data-action="ref-select" data-key="${item.key}" aria-controls="ref-detail" ${s.selected===item.key?'aria-current="true"':''}><span><strong lang="fr">${e(item.word)}</strong><small>${e(item.meaning)}</small></span><span class="badge neutral">${e(item.tag)}</span></button></li>`).join('')}</ul>${hits.length>s.limit?'<button type="button" class="secondary-button reference-more" data-action="ref-more">Show more results</button>':''}`:'<p class="reference-empty">No results. Try a shorter spelling, the infinitive, or an English meaning.</p>';
  }

  function related(view,key,label) {
    return key?`<button type="button" class="secondary-button" data-action="ref-jump" data-view="${view}" data-key="${key}">${label} ${icon('arrow')}</button>`:'';
  }

  function examples(entry) {
    return entry.examples.length?`<section class="reference-section"><h3>Examples</h3><ul class="reference-examples">${entry.examples.map(x=>`<li><p lang="fr"><strong>${e(x.fr)}</strong></p><p class="word-translation">${e(x.en)}</p>${listen(x.fr,false)}</li>`).join('')}</ul>${entry.examples.some(x=>x.status.endsWith('_unreviewed'))?'<p class="reference-note">Includes a course-bank example awaiting editorial review.</p>':''}</section>`:'';
  }

  function inflections(rows,caption,labels) {
    return rows?.length?`<div class="reference-table"><table><caption>${caption}</caption><thead><tr><th scope="col">${labels[0]}</th><th scope="col">Form and audio</th></tr></thead><tbody>${rows.map(x=>`<tr><th scope="row">${e(labels[1](x))}</th><td><strong lang="fr">${e(x.form)}</strong>${x.ipa?` <span class="reference-ipa">${e(x.ipa)}</span>`:''} ${listen(x.form,false)}</td></tr>`).join('')}</tbody></table></div>`:'';
  }

  function verbDetails(entry) {
    const pronominal=entry.key.startsWith('p');
    const variants=new Map();
    for(const v of entry.variants||[]){
      const key=`${v.mood}/${v.tense}/${v.person}`;
      if(!variants.has(key))variants.set(key,[]);
      variants.get(key).push(v);
    }
    const groups=byTense(entry.forms);
    const conjugation=groups.map((forms,i)=>{
      const [{mood,tense}]=forms, title=`${tenseLabels[tense]||tense} · ${moods[mood]||mood}`;
      return `<details class="reference-tense" ${i===0?'open':''}><summary>${e(title)}</summary><div class="reference-table"><table aria-label="${e(title)}"><thead><tr><th scope="col">${mood==='imperative'?'Person':'Subject'}</th><th scope="col">Form and audio</th></tr></thead><tbody>${forms.sort((a,b)=>persons.indexOf(a.person)-persons.indexOf(b.person)).map(f=>{
        const alt=(variants.get(`${f.mood}/${f.tense}/${f.person}`)||[]).concat((f.variants||[]).map(form=>({form})));
        const parts=!f.ipa&&f.parts?.length?f.parts.map(x=>`${x.text} ${x.ipa||'(IPA unavailable)'}`).join(' · '):'';
        return `<tr><th scope="row" lang="fr">${e(f.person.replaceAll('/',' / '))}</th><td><strong lang="fr">${e(f.form)}</strong>${f.ipa?` <span class="reference-ipa">${e(f.ipa)}</span>`:''} ${listen(f.form,false)}${parts?`<small class="reference-note reference-parts">Word IPA: ${e(parts)}</small>`:''}${alt.length?`<details class="reference-variants"><summary>Variants (${alt.length})</summary><ul>${alt.map(v=>`<li><span lang="fr">${e(v.form)}</span>${v.ipa?` <span class="reference-ipa">${e(v.ipa)}</span>`:''} ${listen(v.form,false)}${v.note?`<small class="reference-parts">${e(v.note)}</small>`:''}</li>`).join('')}</ul></details>`:''}</td></tr>`;
      }).join('')}</tbody></table></div></details>`;
    }).join('');
    return `<div class="reference-tags"><span class="badge">Auxiliary: <span lang="fr">${e(entry.auxiliary)}</span></span>${pronominal?'<span class="badge neutral">Pronominal</span>':`<span class="badge neutral">${e(entry.level_code)}</span>`}${entry.impersonal?'<span class="badge neutral">Impersonal</span>':''}</div>${entry.construction?`<div class="reference-tip"><b>Useful construction</b><p>${e(entry.construction)}</p></div>`:''}${examples(entry)}<section class="reference-section"><h3>Conjugation</h3><p class="reference-note">${pronominal?'Includes reflexive pronouns and available agreement variants.':'The subject is shown separately. Audio reads the form in the second column.'}</p>${conjugation}${inflections(entry.participles,'Participles',['Type',x=>x.kind==='present'?'Present participle':`Past · ${featureNames[x.agreement]||x.agreement}`])}</section><section class="reference-section"><h3>Usage notes</h3>${[entry.usage_note,entry.auxiliary_note,entry.agreement_note].filter(Boolean).map(note=>`<p>${e(note)}</p>`).join('')}</section><div class="reference-links">${related('verbs',entry.related_verb,pronominal?'View base verb':'View pronominal form')}${related('dictionary',entry.related_word,'Open in Dictionary')}</div>`;
  }

  function wordDetails(entry) {
    const tags=[...(entry.parts_of_speech||[]),...(entry.genders||[]).map(g=>genderNames[g]||g)];
    return `<div class="reference-tags">${[...new Set(tags)].map(tag=>`<span class="badge neutral">${e(tag)}</span>`).join('')}</div>${examples(entry)}<section class="reference-section"><h3>Word forms and usage</h3>${entry.construction?`<div class="reference-tip"><b>Useful construction</b><p>${e(entry.construction)}</p></div>`:''}${entry.lemmas?.some(l=>l!==entry.word)?`<p>Related dictionary forms: <span lang="fr">${e(entry.lemmas.join(', '))}</span></p>`:''}${inflections(entry.inflections,'Available word forms',['Grammar',x=>featureNames[x.features]||'Base form'])}${entry.usage_note?`<p class="reference-note">${e(entry.usage_note)}</p>`:''}${related('verbs',entry.related_verb,'View full conjugation')}</section>${entry.patterns?.length?`<section class="reference-section"><h3>Sentence patterns to practise</h3>${entry.patterns.map(p=>`<details class="reference-tense"><summary>${e(p.title)}</summary><div class="reference-pattern"><b>${e(p.pattern)}</b><p>${e(p.explanation)}</p><p lang="fr">${e(p.example_fr)}</p><p class="word-translation">${e(p.example_en)}</p>${listen(p.example_fr,false)}</div></details>`).join('')}</section>`:''}<button type="button" class="secondary-button" data-action="lesson" data-day="${entry.day}">Go to Day ${entry.day} ${icon('arrow')}</button>`;
  }

  async function showDetail(kind, focus=false) {
    const s=sessions[kind], token=++s.detailRequest;
    const panel=pane(kind);
    if(!panel)return;
    const entry=s.entries?.find(x=>x.key===s.selected);
    if(!entry){panel.innerHTML=`<div class="reference-placeholder">${icon(kind==='verbs'?'verbs':'dictionary')}<h2>${kind==='verbs'?'Choose a verb':'Choose a word'}</h2><p>Search or choose one of the suggestions to open its reference.</p></div>`;return;}
    panel.innerHTML=`<p class="reference-note" role="status">Loading ${e(entry.word)}…</p>`;
    const path=`${kind}-${entry.shard}`;
    if(!shards.has(path))shards.set(path,read(path).catch(error=>{shards.delete(path);throw error;}));
    try{
      const record=(await shards.get(path))[entry.key];
      if(!record)throw Error('Missing entry');
      if(token!==s.detailRequest||pane(kind)!==panel)return;
      panel.innerHTML=`<header class="reference-entry-head"><h2 lang="fr" tabindex="-1">${e(record.word)}</h2><p>${e(record.meaning)}</p><div class="reference-pronunciation">${record.ipa?`<span class="reference-ipa">${e(record.ipa)}</span>`:'<small class="reference-note">IPA unavailable</small>'}${listen(record.word)}</div></header>${kind==='verbs'?verbDetails(record):wordDetails(record)}`;
      if(focus){panel.querySelector('h2').focus({preventScroll:true});if(window.matchMedia('(max-width: 1050px)').matches)panel.scrollIntoView({block:'start'});}
    }catch{
      if(token===s.detailRequest&&pane(kind)===panel)panel.innerHTML='<p role="alert">Could not load this entry.</p><button class="secondary-button" data-action="ref-detail-retry">Try again</button>';
    }
  }

  async function mount(kind, focus=false) {
    const s=sessions[kind];
    updateResults(kind);
    if(!s.entries){
      s.promise ||= read(kind).then(entries=>{s.entries=entries.map(prepareLookup);s.error=false;}).catch(()=>{s.error=true;}).finally(()=>{s.promise=null;});
      await s.promise;
      updateResults(kind);
    }
    await showDetail(kind,focus);
  }

  function query(kind,value){const s=sessions[kind];s.query=value;s.limit=pageSize;updateResults(kind);}
  function more(kind){sessions[kind].limit+=pageSize;updateResults(kind);root(kind)?.querySelector('.reference-results li:nth-child('+ (sessions[kind].limit-pageSize+1) +') button')?.focus();}
  function select(kind,key){sessions[kind].selected=key;updateResults(kind);void showDetail(kind,true);}
  function first(kind){const s=sessions[kind];const result=searchReference(s.entries||[],s.query,kind)[0];if(result)select(kind,result.key);}
  function jump(kind,key){const s=sessions[kind];s.query='';s.limit=pageSize;s.selected=key;}
  function retry(kind){sessions[kind].error=false;void mount(kind);}
  return {screen,mount,query,more,select,first,jump,retry,retryDetail:kind=>void showDetail(kind,true)};
}
