"""Build the 1,000-entry conversational word bank from the checked-in TSV.

Examples are original teaching drafts and explicitly marked as such. IPA comes
from ipa-dict/fr_FR; seven gaps have independently entered overrides below.
"""
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
IPA_OVERRIDES = {
    'l’un': '/lœ̃/', 'd’autres': '/dotʁ/', 'afin de': '/afɛ̃ də/',
    'internet': '/ɛ̃tɛʁnɛt/', 'l’une': '/lyn/', 'quant à': '/kɑ̃t a/',
    'etc': '/ɛt seteʁa/',
    'au revoir': '/o ʁəvwaʁ/', 's’il vous plaît': '/sil vu plɛ/',
    'en revanche': '/ɑ̃ ʁəvɑ̃ʃ/', 'contre-argument': '/kɔ̃tʁ aʁɡymɑ̃/',
}
REGULAR_IR = {'agir', 'saisir', 'établir', 'réunir', 'réagir', 'ralentir', 'remplir', 'choisir', 'réussir', 'finir'}
IRREGULAR_ER = {'aller', 'envoyer', 'appeler', 'rappeler', 'jeter', 'acheter', 'lever', 'enlever', 'soulever', 'mener', 'emmener', 'ramener', 'amener', 'promener', 'élever', 'relever', 'payer', 'essayer', 'appuyer', 'manger', 'changer', 'commencer', 'avancer', 'placer', 'prononcer', 'annoncer', 'espérer', 'préférer', 'considérer', 'posséder', 'répéter', 'créer', 'prier', 'étudier', 'oublier'}
PERSONS = ('je', 'tu', 'il/elle/on', 'nous', 'vous', 'ils/elles')
with (ROOT/'conjugation_overrides.tsv').open(encoding='utf-8') as source:
    IRREGULAR_PRESENT = {row['infinitive']: row for row in csv.DictReader(source, delimiter='\t')}
ENDINGS = {
    'present': ('e', 'es', 'e', 'ons', 'ez', 'ent'),
    'imperfect': ('ais', 'ais', 'ait', 'ions', 'iez', 'aient'),
    'future': ('ai', 'as', 'a', 'ons', 'ez', 'ont'),
    'conditional': ('ais', 'ais', 'ait', 'ions', 'iez', 'aient'),
}

FUNCTION_EXAMPLES = {
    'je': ('Je suis ici.', 'I am here.'), 'tu': ('Tu es ici.', 'You are here.'),
    'il': ('Il arrive demain.', 'He arrives tomorrow.'),
    'elle': ('Elle arrive demain.', 'She arrives tomorrow.'),
    'nous': ('Nous parlons français.', 'We speak French.'),
    'vous': ('Vous avez une question ?', 'Do you have a question?'),
    'ils': ('Ils arrivent demain.', 'They arrive tomorrow.'),
    'elles': ('Elles arrivent demain.', 'They arrive tomorrow.'),
    'le': ('Le train arrive.', 'The train is arriving.'),
    'la': ('La porte est ouverte.', 'The door is open.'),
    'les': ('Les enfants jouent.', 'The children are playing.'),
    'un': ('Un ami arrive.', 'A friend is arriving.'),
    'une': ('Une amie arrive.', 'A friend is arriving.'),
    'de': ('Je viens de Paris.', 'I come from Paris.'),
    'à': ('Je vais à Paris.', 'I am going to Paris.'),
    'et': ('Marie et Paul arrivent.', 'Marie and Paul are arriving.'),
    'mais': ('Je viens, mais je suis en retard.', 'I am coming, but I am late.'),
    'ou': ('Tu veux du thé ou du café ?', 'Do you want tea or coffee?'),
    'avec': ('Je viens avec toi.', 'I am coming with you.'),
    'sans': ('Je pars sans mon sac.', 'I am leaving without my bag.'),
    'pour': ('Ce livre est pour toi.', 'This book is for you.'),
    'dans': ('Le livre est dans le sac.', 'The book is in the bag.'),
    'sur': ('Le livre est sur la table.', 'The book is on the table.'),
    'sous': ('Le chat est sous la table.', 'The cat is under the table.'),
    'qui': ('Qui vient demain ?', 'Who is coming tomorrow?'),
    'quoi': ('Tu veux quoi ?', 'What do you want?'),
    'où': ('Où est la gare ?', 'Where is the station?'),
    'quand': ('Quand pars-tu ?', 'When are you leaving?'),
    'comment': ('Comment allez-vous ?', 'How are you?'),
    'pourquoi': ('Pourquoi pars-tu ?', 'Why are you leaving?'),
    'combien': ('Combien coûte ce livre ?', 'How much does this book cost?'),
    'oui': ('Oui, je comprends.', 'Yes, I understand.'),
    'non': ('Non, merci.', 'No, thank you.'),
    'pas': ('Je ne sais pas.', 'I do not know.'),
    'ne': ('Je ne sais pas.', 'I do not know.'),
    'en': ('J’en veux deux.', 'I want two of them.'),
    'y': ('J’y vais demain.', 'I am going there tomorrow.'),
    'se': ('Elle se lève tôt.', 'She gets up early.'),
    'me': ('Il me parle.', 'He is speaking to me.'),
    'te': ('Je te vois.', 'I see you.'),
    'lui': ('Je lui parle.', 'I speak to him or her.'),
    'on': ('On part demain.', 'We are leaving tomorrow.'),
    'ce': ('Ce livre est intéressant.', 'This book is interesting.'),
    'ça': ('Ça va ?', 'How is it going?'),
    'au': ('Je vais au marché.', 'I am going to the market.'),
    'du': ('Je veux du pain.', 'I want some bread.'),
    'des': ('J’ai des questions.', 'I have some questions.'),
    'être': ('Je suis prêt à partir.', 'I am ready to leave.'),
    'avoir': ('J’ai deux billets.', 'I have two tickets.'),
    'faire': ('Je fais le dîner ce soir.', 'I am making dinner tonight.'),
    'aller': ('Je vais au marché.', 'I am going to the market.'),
    'dire': ('Je vais dire la vérité.', 'I am going to tell the truth.'),
    'voir': ('Je veux voir ce film.', 'I want to see this film.'),
    'parler': ('Nous pouvons parler demain.', 'We can talk tomorrow.'),
    'prendre': ('Je vais prendre le train.', 'I am going to take the train.'),
    'venir': ('Tu peux venir demain.', 'You can come tomorrow.'),
    'pouvoir': ('Je peux vous aider.', 'I can help you.'),
    'vouloir': ('Je veux un café.', 'I want a coffee.'),
    'devoir': ('Je dois partir tôt.', 'I have to leave early.'),
    'savoir': ('Je veux savoir la réponse.', 'I want to know the answer.'),
    'souffrir': ('Il souffre depuis hier.', 'He has been suffering since yesterday.'),
    'mourir': ('Cette plante peut mourir sans eau.', 'This plant can die without water.'),
    'falloir': ('Il faut partir maintenant.', 'We have to leave now.'),
    'boire': ('Je vais boire de l’eau.', 'I am going to drink some water.'),
    'manger': ('Nous allons manger ensemble.', 'We are going to eat together.'),
    'dormir': ('Je vais dormir tôt ce soir.', 'I am going to sleep early tonight.'),
    'acheter': ('Je vais acheter du pain.', 'I am going to buy bread.'),
    'attendre': ('Je vais attendre le bus.', 'I am going to wait for the bus.'),
    'aimer': ('J’aime cette chanson.', 'I like this song.'),
    'écouter': ('J’écoute la radio.', 'I am listening to the radio.'),
    'regarder': ('Je regarde le ciel.', 'I am looking at the sky.'),
    'lire': ('Je vais lire ce livre.', 'I am going to read this book.'),
    'écrire': ('Je vais écrire un message.', 'I am going to write a message.'),
    'apprendre': ('Je vais apprendre le français.', 'I am going to learn French.'),
    'comprendre': ('Je comprends cette question.', 'I understand this question.'),
    'travailler': ('Elle travaille au bureau.', 'She works at the office.'),
    'habiter': ('Nous habitons ici.', 'We live here.'),
    'connaître': ('Je connais cette ville.', 'I know this city.'),
    'sortir': ('Je vais sortir ce soir.', 'I am going out tonight.'),
    'partir': ('Je vais partir demain.', 'I am leaving tomorrow.'),
    'revenir': ('Elle va revenir bientôt.', 'She will come back soon.'),
    'mettre': ('Je vais mettre le livre sur la table.', 'I am going to put the book on the table.'),
    'donner': ('Je vais donner le livre à Paul.', 'I am going to give the book to Paul.'),
    'demander': ('Je vais demander de l’aide.', 'I am going to ask for help.'),
    'répondre': ('Je vais répondre à votre question.', 'I am going to answer your question.'),
    'finir': ('Je vais finir ce travail.', 'I am going to finish this work.'),
    'choisir': ('Nous devons choisir une date.', 'We need to choose a date.'),
    'envoyer': ('Je vais envoyer un message.', 'I am going to send a message.'),
    'payer': ('Je vais payer l’addition.', 'I am going to pay the bill.'),
    'ouvrir': ('Je vais ouvrir la fenêtre.', 'I am going to open the window.'),
    'fermer': ('Je vais fermer la porte.', 'I am going to close the door.'),
    'jouer': ('Les enfants vont jouer dehors.', 'The children are going to play outside.'),
    'courir': ('Je vais courir dans le parc.', 'I am going to run in the park.'),
    'conduire': ('Je peux conduire ce soir.', 'I can drive tonight.'),
    'perdre': ('Je ne veux pas perdre ce billet.', 'I do not want to lose this ticket.'),
    'gagner': ('Notre équipe peut gagner.', 'Our team can win.'),
    'changer': ('Je vais changer de train.', 'I am going to change trains.'),
    'chercher': ('Je cherche mes clés.', 'I am looking for my keys.'),
    'trouver': ('Je veux trouver une solution.', 'I want to find a solution.'),
    'utiliser': ('Je vais utiliser cette carte.', 'I am going to use this card.'),
    'venir': ('Tu peux venir demain.', 'You can come tomorrow.'),
}


def infer_pos(word, meaning, existing):
    if existing:
        return existing[2], existing[3]
    if meaning.startswith('to ') and (word.endswith(('er', 'ir', 're', 'oir')) or word == 'être'):
        return 'verb', None
    return 'unclassified', None


def example(word, meaning, pos, gender):
    if word in FUNCTION_EXAMPLES:
        return FUNCTION_EXAMPLES[word]
    if pos == 'verb':
        # A grammatical citation sentence until a contextual example is edited.
        return (f'Comment utilise-t-on le verbe « {word} » ?', f'How is the verb “{word}” ({meaning.split(";")[0]}) used?')
    if pos == 'noun' and gender:
        article = 'le' if gender == 'm' else 'la'
        if word[0].lower() in 'aeiouéèêëîïôùûü' or word.startswith('h'):
            article = 'l’'
            phrase = article + word
        else:
            phrase = article + ' ' + word
        return (f'Je cherche {phrase}.', f'I am looking for the {meaning.split(";")[0].split("/")[0]}.')
    # Quotation makes the fallback grammatical even for an inflected or
    # ambiguous form. A later editorial pass should replace it with usage.
    return (f'Comment emploie-t-on « {word} » ?', f'How do you use “{word}” ({meaning.split(";")[0]})?')


def add_regular_conjugations(conn, infinitive, meaning, level):
    if infinitive in IRREGULAR_PRESENT:
        row = IRREGULAR_PRESENT[infinitive]
        cur = conn.execute('INSERT INTO verbs(infinitive,english,group_name,auxiliary,level_code) VALUES (?,?,?,?,?)',
                           (infinitive, meaning.removeprefix('to '), 'irregular', row['auxiliary'], level))
        for person, key in zip(PERSONS, ('je','tu','il_elle_on','nous','vous','ils_elles')):
            conn.execute('INSERT INTO conjugations(verb_id,mood,tense,person,form) VALUES (?,"indicative","present",?,?)',
                         (cur.lastrowid, person, row[key]))
        return cur.lastrowid
    if infinitive.endswith('er') and infinitive not in IRREGULAR_ER and not infinitive.endswith(('ger', 'cer', 'yer', 'eler', 'eter')) and 'é' not in infinitive[:-2] and 'è' not in infinitive[:-2]:
        group = '-er'
    elif infinitive in REGULAR_IR:
        group = '-ir'
    else:
        return None
    cur = conn.execute('INSERT INTO verbs(infinitive,english,group_name,auxiliary,level_code) VALUES (?,?,?,?,?)',
                       (infinitive, meaning.removeprefix('to '), group, 'avoir', level))
    for tense, suffixes in ENDINGS.items():
        for person, ending in zip(PERSONS, suffixes):
            stem = infinitive if tense in ('future', 'conditional') else infinitive[:-2]
            if group == '-ir' and tense in ('present', 'imperfect'):
                ending = (('is','is','it','issons','issez','issent') if tense == 'present' else ('issais','issais','issait','issions','issiez','issaient'))[PERSONS.index(person)]
            form = stem + ending
            conn.execute('INSERT INTO conjugations(verb_id,mood,tense,person,form) VALUES (?,?,?,?,?)',
                         (cur.lastrowid, 'conditional' if tense == 'conditional' else 'indicative',
                          'present' if tense == 'conditional' else tense, person, form))
    return cur.lastrowid


def apply(conn):
    rows = list(csv.DictReader((ROOT/'conversation_words.tsv').open(encoding='utf-8'), delimiter='\t'))
    assert len(rows) == 1000 and len({r['french'] for r in rows}) == 1000
    for rank, row in enumerate(rows, 1):
        word, meaning = row['french'], row['meaning_en']
        ipa = row['ipa'] or IPA_OVERRIDES.get(word)
        assert ipa and ipa.startswith('/') and ipa.endswith('/'), (rank, word, ipa)
        current = conn.execute('SELECT id,level_code,part_of_speech,gender FROM lexemes WHERE french=? ORDER BY CASE WHEN part_of_speech="verb" THEN 0 ELSE 1 END LIMIT 1', (word,)).fetchone()
        pos, gender = infer_pos(word, meaning, current)
        day = 15 + (rank - 1) // 4
        if current:
            day = max(day, {'A0': 1, 'A1': 15, 'A2': 85, 'B1': 155,
                            'B2': 239, 'C1': 309, 'C2': 365}[current[1]])
        level = conn.execute('SELECT u.level_code FROM lessons l JOIN units u ON u.id=l.unit_id WHERE l.day_number=?', (day,)).fetchone()[0]
        if current:
            lexeme_id = current[0]
            conn.execute('UPDATE lexemes SET ipa=COALESCE(ipa,?) WHERE id=?', (ipa, lexeme_id))
        else:
            cur = conn.execute('INSERT INTO lexemes(french,english,part_of_speech,gender,level_code,ipa) VALUES (?,?,?,?,?,?)', (word, meaning, pos, gender, level, ipa))
            lexeme_id = cur.lastrowid
        verb_id = None
        status = 'not_applicable'
        if pos == 'verb':
            hit = conn.execute('SELECT id FROM verbs WHERE infinitive=?', (word,)).fetchone()
            verb_id = hit[0] if hit else add_regular_conjugations(conn, word, meaning, level)
            status = 'available' if verb_id else 'pending_review'
        fr, en = example(word, meaning, pos, gender)
        conn.execute('INSERT INTO conversation_words(rank,lexeme_id,french,meaning_en,ipa,example_fr,example_en,example_status,verb_id,conjugation_status,introduced_day) VALUES (?,?,?,?,?,?,?,?,?,?,?)',
                     (rank, lexeme_id, word, meaning, ipa, fr, en, 'draft', verb_id, status, day))
        conn.execute('INSERT OR IGNORE INTO lesson_lexemes(lesson_id,lexeme_id) VALUES (?,?)', (day, lexeme_id))
        for direction, front, back in (('fr_en', word, meaning), ('en_fr', meaning, word)):
            conn.execute('INSERT INTO flashcards(lesson_id,lexeme_id,front,back,direction,tags_json) VALUES (?,?,?,?,?,?)',
                         (day, lexeme_id, front, back, direction, json.dumps(['conversation_1000', level])))


def apply_extra(conn):
    """Add a second bank with corpus usage examples and complete verb links."""
    rows = list(csv.DictReader((ROOT/'conversation_words_extra.tsv').open(encoding='utf-8'), delimiter='\t'))
    assert len(rows) == 1000 and len({row['french'] for row in rows}) == 1000
    for offset, row in enumerate(rows):
        rank = 1001 + offset
        word, meaning, ipa = row['french'], row['meaning_en'], row['ipa']
        pos, gender = row['part_of_speech'], row['gender'] or None
        assert pos in {'noun', 'verb', 'adjective', 'adverb'}
        assert ipa.startswith('/') and ipa.endswith('/')
        assert re.search(r'(?<!\w)' + re.escape(word) + r'(?!\w)', row['example_fr'], re.IGNORECASE), word
        assert row['example_en'].strip() and meaning.strip()
        assert not conn.execute('SELECT 1 FROM lexemes WHERE french=?', (word,)).fetchone(), word
        day = 15 + offset // 4
        level = conn.execute('SELECT u.level_code FROM lessons l JOIN units u ON u.id=l.unit_id WHERE l.day_number=?', (day,)).fetchone()[0]
        cur = conn.execute('INSERT INTO lexemes(french,english,part_of_speech,gender,level_code,ipa,notes) VALUES (?,?,?,?,?,?,?)',
                           (word, meaning, pos, gender, level, ipa, f'Corpus usage example; subtitle frequency rank {row["frequency_rank"]}.'))
        lexeme_id = cur.lastrowid
        verb_id = None
        if pos == 'verb':
            hit = conn.execute('SELECT id FROM verbs WHERE infinitive=?', (word,)).fetchone()
            verb_id = hit[0] if hit else add_regular_conjugations(conn, word, meaning, level)
            assert verb_id, f'Missing checked present conjugation for {word}'
        conn.execute('INSERT INTO conversation_words(rank,lexeme_id,french,meaning_en,ipa,example_fr,example_en,example_status,example_source,verb_id,conjugation_status,introduced_day) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',
                     (rank, lexeme_id, word, meaning, ipa, row['example_fr'], row['example_en'],
                      'corpus_unreviewed', 'Tatoeba French–English pairs via desmondyeoh/data-eng-fra',
                      verb_id, 'available' if verb_id else 'not_applicable', day))
        conn.execute('INSERT INTO lesson_lexemes(lesson_id,lexeme_id) VALUES (?,?)', (day, lexeme_id))
        for direction, front, back in (('fr_en', word, meaning), ('en_fr', meaning, word)):
            conn.execute('INSERT INTO flashcards(lesson_id,lexeme_id,front,back,direction,tags_json) VALUES (?,?,?,?,?,?)',
                         (day, lexeme_id, front, back, direction, json.dumps(['conversation_2000', level])))
