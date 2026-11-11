"""Build small search indexes and lazy-loaded reference detail files."""
import json


# Original examples for frequently studied verbs and verbs without a bank example.
EXAMPLES = {
    'être': [('Nous sommes prêts à partir.', 'We are ready to leave.'), ('Hier, elle était à la bibliothèque.', 'Yesterday, she was at the library.')],
    'avoir': [('J’ai besoin d’un dictionnaire.', 'I need a dictionary.'), ('Nous avons eu le temps de déjeuner.', 'We had time to eat lunch.')],
    'aller': [('Je vais à la gare en bus.', 'I go to the station by bus.'), ('Elles sont allées au marché.', 'They went to the market.')],
    'faire': [('Vous faites du café le matin ?', 'Do you make coffee in the morning?'), ('J’ai fait les courses hier.', 'I went grocery shopping yesterday.')],
    'pouvoir': [('Vous pouvez ouvrir la fenêtre ?', 'Can you open the window?'), ('Je pourrai vous aider demain.', 'I will be able to help you tomorrow.')],
    'vouloir': [('Je voudrais un verre d’eau.', 'I would like a glass of water.'), ('Ils veulent apprendre le français.', 'They want to learn French.')],
    'devoir': [('Je dois partir avant huit heures.', 'I have to leave before eight o’clock.'), ('Nous avons dû attendre le train.', 'We had to wait for the train.')],
    'prendre': [('Nous prenons le métro tous les jours.', 'We take the metro every day.'), ('Elle a pris son manteau.', 'She took her coat.')],
    'venir': [('Tu viens avec nous ?', 'Are you coming with us?'), ('Elle est venue en train.', 'She came by train.')],
    'manger': [('Nous mangeons ensemble le vendredi.', 'We eat together on Fridays.'), ('J’ai mangé une pomme.', 'I ate an apple.')],
    'finir': [('Nous finissons à dix-sept heures.', 'We finish at five in the afternoon.'), ('Elle finira le travail demain.', 'She will finish the work tomorrow.')],
    'parler': [('Je parle à ma voisine.', 'I am talking to my neighbour.'), ('Nous avons parlé du voyage.', 'We talked about the trip.')],
    'aimer': [('J’aime lire dans le train.', 'I like reading on the train.'), ('Elle aime les films français.', 'She likes French films.')],
    'sortir': [('Elle est sortie à midi.', 'She went out at noon.'), ('Elle a sorti les clés de son sac.', 'She took the keys out of her bag.')],
    'falloir': [('Il faut fermer la porte.', 'We need to close the door.'), ('Il faut que tu répondes avant midi.', 'You need to reply before noon.')],
    'comparer': [('Elle compare les prix avant d’acheter.', 'She compares prices before buying.'), ('Nous avons comparé les deux réponses.', 'We compared the two answers.')],
    'téléphoner': [('Je téléphone à mon frère le dimanche.', 'I call my brother on Sundays.'), ('Nous lui téléphonerons demain.', 'We will call him tomorrow.')],
    'rougir': [('Il rougit quand on le complimente.', 'He blushes when someone compliments him.')],
    'grossir': [('Sur l’écran, les caractères grossissent quand on zoome.', 'On the screen, the characters get bigger when you zoom in.')],
    'maigrir': [('Le chat a maigri depuis le printemps.', 'The cat has lost weight since spring.')],
    'vieillir': [('Le bois vieillit différemment à l’extérieur.', 'Wood ages differently outdoors.')],
    'dépêcher': [('La rédaction a dépêché une journaliste sur place.', 'The newsroom dispatched a reporter to the scene.')],
    'promener': [('Nous promenons le chien avant le dîner.', 'We walk the dog before dinner.')],
    'se lever': [('Je me lève à sept heures.', 'I get up at seven.'), ('Elle s’est levée plus tôt ce matin.', 'She got up earlier this morning.')],
    'se coucher': [('Tu te couches tard le samedi.', 'You go to bed late on Saturdays.')],
    'se réveiller': [('Les enfants se réveillent tôt.', 'The children wake up early.')],
    'se laver': [('Elle se lave les mains avant le repas.', 'She washes her hands before the meal.')],
    's’habiller': [('Nous nous habillons avant de sortir.', 'We get dressed before going out.')],
    'se préparer': [('Je me prépare pour l’entretien.', 'I am getting ready for the interview.')],
    's’arrêter': [('Le bus s’arrête devant la gare.', 'The bus stops in front of the station.')],
    'se reposer': [('Elles se reposent après la marche.', 'They rest after the walk.')],
    's’appeler': [('Comment vous appelez-vous ?', 'What is your name?')],
    'se souvenir': [('Je me souviens de ce quartier.', 'I remember this neighbourhood.'), ('Tu te souviens de notre premier cours ?', 'Do you remember our first lesson?')],
    's’asseoir': [('Asseyez-vous près de la fenêtre.', 'Sit by the window.')],
    'se concentrer': [('Je me concentre sur la première question.', 'I am focusing on the first question.')],
    'se promener': [('Nous nous promenons dans le parc.', 'We are taking a walk in the park.')],
    'se dépêcher': [('Dépêche-toi, le train arrive !', 'Hurry up, the train is coming!')],
}

CONSTRUCTIONS = {
    'avoir': 'avoir besoin de + noun or infinitive', 'aller': 'aller à / au / aux + destination; aller + infinitive for a near future',
    'parler': 'parler à quelqu’un (to someone); parler de quelque chose (about something)',
    'téléphoner': 'téléphoner à quelqu’un; lui téléphoner', 'devoir': 'devoir + infinitive for an obligation',
    'pouvoir': 'pouvoir + infinitive for ability or permission', 'vouloir': 'vouloir + infinitive; je voudrais for a polite request',
    'se souvenir': 'se souvenir de quelqu’un / de quelque chose', 'se concentrer': 'se concentrer sur + noun',
}


def export_reference(out, conversation, lexemes, base_verbs, pronominal, sentence_patterns):
    folder = out/'reference'
    folder.mkdir(exist_ok=True)

    def write(name, obj):
        (folder/f'{name}.json').write_text(json.dumps(obj,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')

    def bank_example(word):
        return dict(fr=word['example_fr'],en=word['example_en'],status=word['example_status'])

    words = {word['french']:word for word in conversation}
    linked = {}
    for word in conversation:
        if word['verb_id'] is not None:
            linked.setdefault(word['verb_id'],[]).append(word)
    pronominal_keys = {word['base_verb_id']:f'p{word["id"]}' for word in pronominal}
    lexeme_ids = {word['french']:word['id'] for word in lexemes}
    pattern_map = {p['id']:{k:p[k] for k in ('title','pattern','explanation','example_fr','example_en')} for p in sentence_patterns}
    base_map = {v['id']:v for v in base_verbs}
    verb_index, verb_shards, word_index, word_shards = [], {}, [], {}

    def append(index, shards, record, aliases, terms, size):
        shard = len(index)//size
        index.append([record['key'], record['word'], record['meaning'], record['ipa'], shard, terms, sorted(set(aliases)-{record['word']})])
        shards.setdefault(shard,{})[record['key']] = record

    for v in base_verbs:
        lemma = v['infinitive']
        examples = [dict(fr=fr,en=en,status='authored') for fr,en in EXAMPLES.get(lemma,EXAMPLES.get('se souvenir',[]) if lemma=='souvenir' else [])]
        examples += [bank_example(w) for w in sorted(linked.get(v['id'],[]),key=lambda w:w['french']!=lemma)[:1]]
        record = {**v,'key':f'v{v["id"]}','word':lemma,'meaning':v['english'],'ipa':v['infinitive_ipa'],
                  'examples':examples[:3],'construction':CONSTRUCTIONS.get(lemma),'related_verb':pronominal_keys.get(v['id']),
                  'related_word':f'w{lexeme_ids[lemma]}' if lemma in lexeme_ids else None}
        aliases = [f[3] for f in v['forms']]+[x['form'] for x in v['variants']+v['participles']]
        append(verb_index,verb_shards,record,aliases,v['level_code'],24)

    for v in pronominal:
        lemma = v['lemma']
        base = base_map[v['base_verb_id']]
        record = {**v,'key':f'p{v["id"]}','word':lemma,'meaning':v['meaning_en'],'ipa':None,'auxiliary':'être',
                  'examples':[dict(fr=fr,en=en,status='authored') for fr,en in EXAMPLES[lemma]],
                  'construction':CONSTRUCTIONS.get(lemma),'related_verb':f'v{base["id"]}','related_word':None}
        aliases = [form for f in v['forms'] for form in [f['form'],*f['variants']]]
        append(verb_index,verb_shards,record,aliases,base['level_code'],24)

    for word in lexemes:
        w = words[word['french']]
        verb_id = w['verb_id']
        record = {**word,'key':f'w{word["id"]}','word':word['french'],'meaning':w['meaning_en'],'ipa':w['ipa'],
                  'examples':[bank_example(w)],'patterns':[pattern_map[i] for i in word['sentence_pattern_ids'][:3]],
                  'construction':CONSTRUCTIONS.get(word['french']), 'day':w['introduced_day'],
                  'related_verb':f'v{verb_id}' if verb_id is not None else None}
        append(word_index,word_shards,record,[i['form'] for i in word['inflections']]+word['lemmas'],word['part_of_speech'],120)

    for kind, index, shards in [('verbs',verb_index,verb_shards),('dictionary',word_index,word_shards)]:
        write(kind,index)
        for n,records in shards.items(): write(f'{kind}-{n}',records)
