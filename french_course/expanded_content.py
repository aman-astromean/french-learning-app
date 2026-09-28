"""Original teaching material layered over the 420-day syllabus.

Drive worksheets informed topic order only. Their text and exercises are not copied.
IPA targets are a broad metropolitan model; regional realizations differ.
"""
import json

# category, grapheme, target IPA, example, example IPA, translation, articulation, contrast
PRONUNCIATION = {
 1:[('letter name','A','/a/','a','/a/','letter A','Open your mouth; keep the tongue low.',''),('letter name','B','/be/','bé','/be/','letter B','Close the lips for /b/, then release into /e/.',''),('letter name','C','/se/','cé','/se/','letter C','Start with an /s/ hiss, then /e/.',''),('letter name','G','/ʒe/','gé','/ʒe/','letter G','Voice the middle sound, as in French je.','C /se/'),('letter name','H','/aʃ/','ache','/aʃ/','letter H','The name contains /ʃ/; h itself is not sounded in hôtel.',''),('letter name','I','/i/','i','/i/','letter I','Spread the lips and raise the front of the tongue.','')],
 2:[('letter name','J','/ʒi/','ji','/ʒi/','letter J','Voice /ʒ/ before the /i/ vowel.','G /ʒe/'),('letter name','R','/ɛʁ/','erre','/ɛʁ/','letter R','The French /ʁ/ is made near the back of the mouth.',''),('letter name','U','/y/','u','/y/','letter U','Say /i/ while rounding the lips; avoid English oo.','OU /u/'),('letter name','W','/dublə ve/','double vé','/dublə ve/','letter W','Two words form the letter name.','V /ve/'),('letter name','Y','/i ɡʁɛk/','i grec','/i ɡʁɛk/','letter Y','Say the two words i grec.',''),('letter name','Z','/zɛd/','zède','/zɛd/','letter Z','Voice the /z/ at the start.','')],
 3:[('oral vowel','a','/a/','ami','/ami/','friend','Open jaw, tongue low; hold one clear vowel.','i /i/'),('oral vowel','i','/i/','ici','/isi/','here','Smile slightly and keep the tongue high in front.','u /y/'),('oral vowel','o','/o/','mot','/mo/','word','Round lips; the final t is silent here.','a /a/'),('oral vowel','ou','/u/','vous','/vu/','you','Round lips and lift the tongue toward the back.','u /y/'),('oral vowel','u','/y/','tu','/ty/','you','Keep /i/ tongue position while rounding lips.','ou /u/')],
 4:[('vowel spelling','é','/e/','été','/ete/','summer','Higher, tenser e; avoid a diphthong.','è /ɛ/'),('vowel spelling','è','/ɛ/','père','/pɛʁ/','father','Lower jaw a little more than /e/.','é /e/'),('vowel spelling','ê','/ɛ/','fête','/fɛt/','party','Usually open /ɛ/ in this common word.','é /e/'),('vowel spelling','e','/ə/','le','/lə/','the','A reduced central vowel; it may disappear in fast speech.','è /ɛ/'),('vowel spelling','ç','/s/','garçon','/ɡaʁsɔ̃/','boy','Cedilla keeps c as /s/ before o.','c in car /k/'),('vowel spelling','ë','/ɛ/','Noël','/nɔ.ɛl/','Christmas','Diaeresis separates the adjacent vowels into syllables.','')],
 5:[('consonant','ch','/ʃ/','chat','/ʃa/','cat','Push air through a narrow channel behind the teeth; final t is silent.','j /ʒ/'),('consonant','j','/ʒ/','jour','/ʒuʁ/','day','Same constriction as /ʃ/ with vocal-fold vibration.','ch /ʃ/'),('consonant','r','/ʁ/','rue','/ʁy/','street','Make friction near the back of the mouth.',''),('final consonant','t','∅','petit','/pəti/','small','Do not pronounce the final t in petit alone.','petite /pətit/'),('final consonant','s','∅','vous','/vu/','you','The final s is silent in isolation.','vous avez /vu.z‿ave/'),('consonant','gn','/ɲ/','montagne','/mɔ̃taɲ/','mountain','Raise the middle of your tongue toward the palate.','')],
 6:[('nasal vowel','on','/ɔ̃/','bon','/bɔ̃/','good','Let air pass through nose and mouth; do not add an n sound.','beau /bo/'),('nasal vowel','an/en','/ɑ̃/','enfant','/ɑ̃fɑ̃/','child','Lower the tongue and nasalize the vowel.','a /a/'),('nasal vowel','in/ain','/ɛ̃/','pain','/pɛ̃/','bread','Open front vowel with nasal airflow; do not finish with n.','paix /pɛ/'),('nasal vowel','un','/œ̃/','un','/œ̃/','one','Some varieties merge this with /ɛ̃/; listen for both.','in /ɛ̃/'),('sound pair','oi','/wa/','moi','/mwa/','me','Move from /w/ into /a/.',''),('sound pair','eu','/ø/','deux','/dø/','two','Round lips with the tongue toward the front.','')],
 8:[('number','0–3','/zeʁo œ̃ dø tʁwa/','zéro, un, deux, trois','/zeʁo œ̃ dø tʁwa/','zero to three','Count slowly; keep each number distinct.',''),('number','4–6','/katʁ sɛ̃k sis/','quatre, cinq, six','/katʁ sɛ̃k sis/','four to six','Nasalize cinq, but keep the final /k/.',''),('number','7–10','/sɛt ɥit nœf dis/','sept, huit, neuf, dix','/sɛt ɥit nœf dis/','seven to ten','Pronounce the final consonants shown in these isolated forms.','')],
 9:[('number','11–13','/ɔ̃z duz tʁɛz/','onze, douze, treize','/ɔ̃z duz tʁɛz/','eleven to thirteen','Listen for the final voiced /z/.',''),('number','14–16','/katɔʁz kɛ̃z sɛz/','quatorze, quinze, seize','/katɔʁz kɛ̃z sɛz/','fourteen to sixteen','Quinze starts with a nasal vowel.',''),('number','17–20','/disɛt dizɥit diznœf vɛ̃/','dix-sept, dix-huit, dix-neuf, vingt','/disɛt dizɥit diznœf vɛ̃/','seventeen to twenty','Observe the linking /z/ in dix-huit and dix-neuf.','')],
 10:[('number','20, 30','/vɛ̃ tʁɑ̃t/','vingt, trente','/vɛ̃ tʁɑ̃t/','twenty, thirty','The vowel in vingt is nasal.',''),('number','40, 50','/kaʁɑ̃t sɛ̃kɑ̃t/','quarante, cinquante','/kaʁɑ̃t sɛ̃kɑ̃t/','forty, fifty','Keep the final /t/ in each of these tens.',''),('number','21','/vɛ̃.t‿e œ̃/','vingt et un','/vɛ̃.t‿e œ̃/','twenty-one','The t is heard in vingt et un.','vingt /vɛ̃/')],
 11:[('number','70','/swasɑ̃t dis/','soixante-dix','/swasɑ̃t dis/','seventy','Literally sixty-ten; do not say septante in the metropolitan model.',''),('number','80','/katʁə vɛ̃/','quatre-vingts','/katʁə vɛ̃/','eighty','The plural s is silent in isolation.','quatre-vingt-un'),('number','90','/katʁə vɛ̃ dis/','quatre-vingt-dix','/katʁə vɛ̃ dis/','ninety','Build eighty plus ten.',''),('number','100','/sɑ̃/','cent','/sɑ̃/','one hundred','Nasalize the vowel; final t is silent here.','')],
 12:[('pronoun','je','/ʒə/','je','/ʒə/','I','The vowel may reduce in connected speech.',''),('pronoun','tu','/ty/','tu','/ty/','you, familiar singular','Rounded front /y/, different from tout /u/.',''),('pronoun','nous','/nu/','nous','/nu/','we','Final s is silent alone.','vous /vu/'),('verb form','suis','/sɥi/','je suis','/ʒə sɥi/','I am','Practice the glide /ɥ/ after /s/.',''),('verb form','êtes','/ɛt/','vous êtes','/vu.z‿ɛt/','you are','Notice the linking /z/ in vous êtes.','')],
 13:[('sentence rhythm','Je suis ici.','/ʒə sɥi isi/','Je suis ici.','/ʒə sɥi isi/','I am here.','Group words into one short phrase; stress the end.',''),('question intonation','Tu es ici ?','/ty ɛ isi/','Tu es ici ?','/ty ɛ isi/','Are you here?','For a yes/no question, raise the pitch toward the end.',''),('elision','j’','/ʒ/','J’ai un livre.','/ʒe œ̃ livʁ/','I have a book.','Je loses its vowel before the vowel of ai.','je suis')]
}

# Daily teaching progression: concepts, worked examples, discrimination and guided tasks.
# The labels and examples are original and intentionally begin with sounds, not dialogue.
A0 = {
 1:{'goal':'Name A–I and distinguish a letter name from the sound a letter makes inside a word.','steps':[
   ('Letter names','A is called /a/, B is /be/, C is /se/. A letter name is what you say when spelling; it is not a promise that the letter always sounds the same in words.','A, B, C → /a/, /be/, /se/'),
   ('Two jobs for C','The name C is /se/. In café, c begins with /k/; in ici, c sounds /s/. The next letter helps determine the sound.','café /kafe/ · ici /isi/'),
   ('Spell in chunks','Read A B C, then D E F, then G H I. Pause after each group and point at the printed letter you name.','D /de/ · E /ə/ · F /ɛf/'),
   ('Check your ear','G /ʒe/ and J /ʒi/ share /ʒ/ but have different vowels. Today learn G; J follows tomorrow.','G /ʒe/')],
   'checks':[('Which is the French name of B?','/be/','/b/','/de/','B is /be/; /b/ is a consonant sound inside words.'),('Which word begins with /k/?','café','ici','été','The c in café is /k/ before a.'),('Which is a letter name?','/ɛf/','/f/','/ʃ/','F is named /ɛf/; the consonant alone is /f/.')],
   'practice':'Point to A–I and name each letter aloud; spell the letters C–A–F–É without trying to read the whole word.'},
 2:{'goal':'Name J–Z and find letters with two-word names and unfamiliar vowels.','steps':[
   ('Names J–R','J is /ʒi/, K /ka/, L /ɛl/, M /ɛm/, N /ɛn/, O /o/, P /pe/, Q /ky/, R /ɛʁ/.','J /ʒi/ · Q /ky/ · R /ɛʁ/'),
   ('Names S–Z','S /ɛs/, T /te/, U /y/, V /ve/, W /dublə ve/, X /iks/, Y /i ɡʁɛk/, Z /zɛd/.','W = double vé · Y = i grec'),
   ('Make French U','Say the vowel /i/ as in ici while keeping your tongue there; round your lips as for /u/. The result is /y/, the French U name.','U /y/ · OU /u/'),
   ('Spell a name','Spell L–U–C using letter names /ɛl y se/. Then read Luc as a separate word: /lyk/.','L–U–C: /ɛl y se/; Luc: /lyk/')],
   'checks':[('Which letter is called /i ɡʁɛk/?','Y','I','W','Y is i grec; I alone is /i/.'),('Which is the name of U?','/y/','/u/','/i/','French U is /y/; OU is /u/.'),('Which letter has the two-word name double vé?','W','V','X','W is double vé; V is vé.')],
   'practice':'Spell your first name with French letter names. Circle letters that have names you cannot yet say confidently.'},
 3:{'goal':'Read clear oral vowels /a i o u y/ in short words.','steps':[
   ('A and I','In ami /ami/, a is open /a/ and i is a high front /i/. Each written vowel contributes a clear beat.','ami /a.mi/ · ici /i.si/'),
   ('O and OU','The o of mot is /o/ and final t is silent. The two letters ou represent one vowel /u/ in vous.','mot /mo/ · vous /vu/'),
   ('U versus OU','U in tu is /y/; ou in tout is /u/. Change the lip and tongue setting to hear a new word.','tu /ty/ · tout /tu/'),
   ('Syllable beats','Tap once for each vowel beat: ami has two /a.mi/; ici has two /i.si/. Do not read every written consonant as an extra beat.','a-mi · i-ci')],
   'checks':[('Which spelling usually gives /u/?','ou','u','i','OU gives /u/ in vous; U gives /y/ in tu.'),('Which word has a silent final t?','mot','ami','ici','Mot is /mo/ in isolation.'),('How many vowel beats are in ami?','two','one','three','Ami is /a.mi/.')],
   'practice':'Alternate tu /ty/ and tout /tu/ five times; record yourself if possible and compare the lip shapes.'},
 4:{'goal':'Recognize accents and separate /e/ from /ɛ/ without assuming every accent changes pronunciation.','steps':[
   ('Acute accent','é commonly marks /e/, as in été /ete/. Keep the tongue high and the sound steady.','été /e.te/'),
   ('Grave and circumflex','è and ê often show open /ɛ/ in père /pɛʁ/ and fête /fɛt/. Lower the jaw slightly compared with /e/.','père /pɛʁ/ · fête /fɛt/'),
   ('Cedilla','ç means c is /s/ before a, o or u: garçon /ɡaʁsɔ̃/. A plain c before a often sounds /k/.','garçon /ɡaʁsɔ̃/ · café /kafe/'),
   ('Other marks','A diaeresis can signal separate vowels: Noël /nɔ.ɛl/. A grave accent on à distinguishes spelling from a, though both sound /a/.','Noël /nɔ.ɛl/ · à /a/')],
   'checks':[('Which spelling is commonly /e/?','é','è','ç','É is /e/ in été.'),('Which word has /ɛ/?','père','été','mot','Père contains open /ɛ/.'),('What does ç do in garçon?','makes c /s/','makes c /k/','adds a syllable','The cedilla keeps /s/ before o.')],
   'practice':'Read été, père, fête and Noël. Mark /e/, /ɛ/ and the syllable boundary before you say each word.'},
 5:{'goal':'Notice common consonant spellings and silent final letters; read words before combining them.','steps':[
   ('CH and J','ch in chat is /ʃ/; j in jour is voiced /ʒ/. Place fingers on your throat to feel voice vibration in /ʒ/.','chat /ʃa/ · jour /ʒuʁ/'),
   ('French R','The common /ʁ/ is produced near the back of the mouth. Practice rue /ʁy/ slowly; clarity matters more than forcing a harsh sound.','rue /ʁy/'),
   ('Final letters','The t of chat and petit, and the s of vous, are silent in these isolated words. This is a pattern with exceptions, not a rule for every final letter.','chat /ʃa/ · petit /pəti/ · vous /vu/'),
   ('Spelling clusters','gn in montagne is /ɲ/. Split the word as /mɔ̃.taɲ/ and listen for the last consonant.','montagne /mɔ̃.taɲ/')],
   'checks':[('Which word has /ʃ/?','chat','jour','rue','CH is /ʃ/ in chat.'),('Which isolated word has a silent final t?','petit','fête','sept','Petit is /pəti/; the other words have audible final /t/.'),('Which spelling represents /ɲ/?','gn','ch','ou','GN is /ɲ/ in montagne.')],
   'practice':'Say chat, jour, petit, vous and montagne. Underline letters that are written but not heard.'},
 6:{'goal':'Distinguish nasal vowels and read frequent vowel pairs without adding a final n.','steps':[
   ('What nasal means','For /ɔ̃/ in bon, air passes through nose and mouth during the vowel. Do not tack an English n onto the end.','bon /bɔ̃/'),
   ('Three common targets','Compare bon /bɔ̃/, enfant /ɑ̃fɑ̃/ and pain /pɛ̃/. These are distinct targets in a broad metropolitan model.','bon /bɔ̃/ · enfant /ɑ̃fɑ̃/ · pain /pɛ̃/'),
   ('Regional variation','Un is often described as /œ̃/; many speakers merge it with /ɛ̃/. Recognize both realizations rather than treating one as wrong.','un /œ̃/ or /ɛ̃/'),
   ('Two more pairs','oi is /wa/ in moi; eu is /ø/ in deux. Read the pair as one target before saying the full word.','moi /mwa/ · deux /dø/')],
   'checks':[('Which word has /ɔ̃/?','bon','pain','moi','Bon is /bɔ̃/.'),('What should you avoid after the vowel in bon?','adding an English n','rounding the lips','voicing b','The nasal vowel itself carries nasal airflow.'),('What is oi in moi?','/wa/','/wi/','/ɔ̃/','Moi is /mwa/.')],
   'practice':'Contrast beau /bo/ with bon /bɔ̃/, then paix /pɛ/ with pain /pɛ̃/. Focus on the vowel, not a final n.'},
 7:{'goal':'Retrieve week-one letters, accents, oral vowels and nasals; discriminate before speaking.','steps':[('Recall','Name A–Z in four groups without looking; mark letters to revisit.','A–F · G–M · N–T · U–Z'),('Contrast','Read tu /ty/ vs tout /tu/, été /ete/ vs père /pɛʁ/, beau /bo/ vs bon /bɔ̃/.','/y/ : /u/ · /e/ : /ɛ/ · /o/ : /ɔ̃/'),('Dictation preparation','Have a partner read letter names or use a future recording; write the letters you hear. Do not infer scores from self-recordings yet.','G /ʒe/ · J /ʒi/'),('Checkpoint','Answer the review questions, then spell your name and read five isolated words. Repeat missed sound families.','chat · ici · tu · bon · été')],
   'checks':[('Which is a letter name rather than a single consonant?','/ɛf/','/f/','/ʃ/','F is called /ɛf/.'),('Which word has /y/?','tu','tout','vous','U in tu is /y/.'),('Which is /pɛ̃/?','pain','paix','père','Pain ends in a nasal vowel.'),('Which written ending is silent in chat?','t','ch','a','Chat is /ʃa/.'),('Which letter name is /ʒi/?','J','G','I','J is /ʒi/.')],
   'practice':'Spell your name, read the five checkpoint words, and note two sounds to revisit.'},
 8:{'goal':'Count 0–10 as isolated words and identify their written forms.','steps':[('Zero through three','Learn zéro /zeʁo/, un /œ̃/, deux /dø/, trois /tʁwa/. Count four objects with one beat per number.','0 zéro · 1 un · 2 deux · 3 trois'),('Four through six','Quatre /katʁ/, cinq /sɛ̃k/, six /sis/ in isolation. Cinq has a nasal vowel and a pronounced final /k/.','4 quatre · 5 cinq · 6 six'),('Seven through ten','Sept /sɛt/, huit /ɥit/, neuf /nœf/, dix /dis/. Their isolated final consonants are audible.','7 sept · 8 huit · 9 neuf · 10 dix'),('Retrieval','Cover the names; write 0–10 from memory. Then count backward from 10. Context can change the endings of six and dix; this drill uses isolated forms.','10 → 0')],
   'checks':[('What is 3?','trois','deux','quatre','Trois is 3.'),('What is 8?','huit','six','neuf','Huit is 8.'),('Which number is zéro?','0','1','10','Zéro names zero.')],
   'practice':'Count eleven objects from zero to ten aloud and write each French word once.'},
 9:{'goal':'Count 11–20 and recognize the 17–19 dix pattern.','steps':[('Eleven to sixteen','These are single words: onze, douze, treize, quatorze, quinze, seize. Memorize in two groups of three.','11 onze · 12 douze · 13 treize · 14 quatorze · 15 quinze · 16 seize'),('Seventeen to nineteen','Build dix-sept, dix-huit, dix-neuf. Dix is pronounced with /z/ before huit and neuf in these compounds.','17 dix-sept · 18 dix-huit · 19 dix-neuf'),('Twenty','Vingt is /vɛ̃/ in isolation. Connect the sound to the nasal vowel studied on day 6.','20 vingt /vɛ̃/'),('Sequence practice','Go 11–20 forward, then 20–11 backward. Separate spelling recall from sound recall.','16 seize → 17 dix-sept')],
   'checks':[('What is 15?','quinze','quatorze','seize','Quinze is fifteen.'),('What is 18?','dix-huit','dix-sept','dix-neuf','Dix-huit is eighteen.'),('What follows seize?','dix-sept','quinze','vingt','Seize is sixteen; dix-sept is seventeen.')],
   'practice':'Write 11–20 from memory, then read each number aloud; circle the three beginning with dix-.'},
 10:{'goal':'Build 20–69 from tens and units, including the special et un pattern.','steps':[('Tens to sixty','Vingt 20, trente 30, quarante 40, cinquante 50, soixante 60. Learn tens as anchors before combining.','20 vingt · 30 trente · 40 quarante · 50 cinquante · 60 soixante'),('Add units','For 22–29, join the ten and unit with a hyphen: vingt-deux, vingt-trois. Repeat for other decades.','22 vingt-deux · 34 trente-quatre'),('One after a ten','In the metropolitan pattern, 21, 31, 41, 51 and 61 use et un: vingt et un, trente et un.','21 vingt et un · 31 trente et un'),('Read real quantities','Read 24, 36, 47, 58, 62 aloud and identify ten + unit. Keep the number words separate from full sentences for now.','24 = vingt-quatre')],
   'checks':[('What is 40?','quarante','trente','cinquante','Quarante is forty.'),('What is 21?','vingt et un','vingt-un','trente et un','Twenty-one uses et un.'),('What is 34?','trente-quatre','quarante-trois','trente-cinq','Thirty-four is thirty plus four.')],
   'practice':'Write and say 24, 31, 43, 56 and 69; explain which parts mean the tens and units.'},
 11:{'goal':'Recognize metropolitan French patterns 70–100 and place quantities in order.','steps':[('Seventy','70 is soixante-dix (60 + 10); 71 is soixante et onze. Continue 72–79 with soixante + 12–19.','70 soixante-dix · 71 soixante et onze · 72 soixante-douze'),('Eighty','80 is quatre-vingts (4 × 20). Its s drops before another number: 81 quatre-vingt-un.','80 quatre-vingts · 81 quatre-vingt-un'),('Ninety','90 is quatre-vingt-dix (80 + 10); 99 is quatre-vingt-dix-neuf. 100 is cent.','90 quatre-vingt-dix · 100 cent'),('Variant awareness','Belgian and Swiss usage may use septante and nonante; the course teaches the metropolitan counting pattern first.','70 septante (regional) · 90 nonante (regional)')],
   'checks':[('What is 70 in the metropolitan pattern?','soixante-dix','quatre-vingts','soixante','Seventy is sixty plus ten.'),('Which form names 80 alone?','quatre-vingts','quatre-vingt-un','quatre-vingt-dix','Quatre-vingts has a final s in isolation.'),('What is 100?','cent','dix','quatre-vingts','Cent is one hundred.')],
   'practice':'Sort 60, 70, 80, 90 and 100; read 71, 81 and 91 slowly from their components.'},
 12:{'goal':'Use subject pronouns with être after mastering sound and number recognition.','steps':[('Person','Je = I; tu = familiar singular you; il/elle = he/she. Nous = we; vous = formal or plural you; ils/elles = they.','je · tu · il/elle · nous · vous · ils/elles'),('Être singular','The present forms change with person: je suis, tu es, il/elle/on est. Do not use a bare English-style verb form.','je suis · tu es · elle est'),('Être plural','Nous sommes, vous êtes, ils/elles sont. In vous êtes, a linking /z/ is heard.','nous sommes · vous êtes · ils sont'),('Meaning before complexity','Pair one pronoun with one verb form. Short combinations come before articles, adjective agreement and longer sentences.','je suis = I am')],
   'checks':[('Which means I am?','je suis','tu es','il est','Je pairs with suis.'),('Which pairs with vous?','êtes','suis','sommes','Vous êtes is you are.'),('Which pronoun can address one person politely?','vous','ils','nous','Vous can be formal singular or plural.')],
   'practice':'Say all six pronoun + être pairs; hide the forms and recall them in a different order.'},
 13:{'goal':'Build a subject + verb + short complement, then ask a simple yes/no question by intonation.','steps':[('Sentence skeleton','Start with subject + conjugated verb + place: Je suis ici. The pronoun je and suis are a practiced pair.','Je suis ici. = I am here.'),('Change the subject','Tu es ici. changes both pronoun and verb. Il est ici. uses the third-person form. Keep the place fixed while changing the pair.','Tu es ici. · Il est ici.'),('Question by intonation','Tu es ici ? can be a yes/no question in conversation with rising intonation. The same written words can be a statement with falling intonation.','Tu es ici. ↗ Tu es ici ?'),('First noun phrase','Un livre means a book; the article belongs with the noun. J’ai un livre adds a new verb; treat it as a model, not a full conjugation lesson yet.','un livre · J’ai un livre.')],
   'checks':[('Which is a complete basic sentence?','Je suis ici.','Je ici.','Suis je ici.','A basic statement needs subject and conjugated verb.'),('Which is a spoken yes/no question?','Tu es ici ? with rising pitch','Tu ici.','Tu es ici. with a mandatory /z/ after tu','Rising intonation can make Tu es ici ? a question.'),('Which means I am here?','Je suis ici.','Tu es ici.','Il est ici.','Je suis ici matches I am here.')],
   'practice':'Make Je suis ici, Tu es ici, and Il est ici. Ask one of them as a question and answer oui or non.'},
 14:{'goal':'Retrieve numbers, pronoun–verb pairs and the first sentence patterns; identify weak spots.','steps':[('Number recall','Write 0–20 from memory; decode 21, 31, 70, 80, 90 and 100 without looking.','17 dix-sept · 21 vingt et un · 80 quatre-vingts'),('Form recall','Match je, tu, il/elle, nous, vous, ils/elles to the six present forms of être.','je suis · nous sommes'),('Sentence transfer','Change Je suis ici. to Tu es ici. and to a yes/no question. Say it before writing it.','Tu es ici ?'),('Reflection','Retake missed sound families from week one. Self-check pronunciation against IPA; recorded model audio remains a later integration.','/y/–/u/ · /e/–/ɛ/ · nasal vowels')],
   'checks':[('What is 19?','dix-neuf','dix-huit','seize','Dix-neuf is nineteen.'),('Which form is 80?','quatre-vingts','quatre-vingt-un','soixante-dix','The isolated 80 is quatre-vingts.'),('Which form pairs with nous?','sommes','sont','êtes','Nous sommes means we are.'),('Which is a complete statement?','Elle est ici.','Elle ici.','Elle sont ici.','Elle takes est.'),('Which expression asks Are you here?','Tu es ici ?','Je suis ici.','Il est ici.','Tu es ici ? with question intonation.')],
   'practice':'Count 0–20 and 20–100 by tens; say three complete sentences; list three concepts to review.'}
}

SOURCES=[
 ('drive-reference:a1-subject-pronouns','A1 subject pronouns and être worksheet','Topic sequencing reference; original examples and checks written independently. Source link stays in the user’s Drive.'),
 ('drive-reference:a1-negation','A1 negation worksheet','Topic map for later A1/A2; source contains errors and is not copied verbatim.'),
 ('drive-reference:a2-passe-compose','A2 passé composé with avoir','Used to check later-level topic order; exercises not copied.'),
 ('drive-reference:b1-subjunctive','B1 subjunctive worksheet','Used as a topic reference only; probability-based simplifications in source are not adopted.'),
 ('https://www.coe.int/en/web/common-european-framework-reference-languages/phonological-competence','CEFR phonological competence','Separates sound articulation from prosody; course tags remain planning labels.')]

REVIEW_TASKS={
 'A1':('Record a short everyday exchange and write 50–80 words. Introduce the situation, ask one clear question and give a relevant answer.','meaning, basic word order, intelligibility, appropriate politeness'),
 'A2':('Role-play a routine problem in two turns, then write 90–130 words explaining what happened and what you will do next.','task completion, past/future time reference, familiar vocabulary, intelligibility'),
 'B1':('Tell a connected personal account for two minutes and write 150–220 words. Explain a choice and support an opinion with a reason and example.','coherence, narrative time, reasons, repair after misunderstanding'),
 'B2':('Prepare a three-minute position and a 230–330-word argument. State a claim, consider an objection, respond with an example and conclude.','argument structure, counterargument, source caution, register, fluency'),
 'C1':('Present two plausible viewpoints in a four-minute briefing and a 350–450-word synthesis. Identify where the viewpoints converge and where they differ; qualify your own conclusion.','synthesis, qualification, cohesive organization, audience fit, precise vocabulary'),
 'C2':('Give a five-minute nuanced response and a 450–600-word analysis for two different audiences. Preserve uncertainty, implication and subtle shifts in register while defending your interpretation.','fine distinctions, rhetorical control, audience adaptation, precision, self-correction')}

def apply(conn):
    conn.executemany('INSERT INTO content_sources(source_url,title,usage_note) VALUES (?,?,?)',SOURCES)
    for day,items in PRONUNCIATION.items():
        for pos,record in enumerate(items,1):
            conn.execute('INSERT INTO pronunciation_items(lesson_id,position,category,grapheme,ipa,example_fr,example_ipa,meaning_en,articulation,contrast) VALUES (?,?,?,?,?,?,?,?,?,?)',(day,pos,*record))
    # Expose every alphabet letter on its lesson day, even where the finer
    # articulation note above covers only a representative subset.
    for index,(letter,name,ipa) in enumerate(conn.execute('SELECT letter,letter_name_fr,ipa FROM alphabet ORDER BY letter').fetchall()):
        day=1 if index<9 else 2
        if conn.execute('SELECT 1 FROM pronunciation_items WHERE lesson_id=? AND grapheme=?',(day,letter)).fetchone():
            continue
        position=conn.execute('SELECT COALESCE(MAX(position),0)+1 FROM pronunciation_items WHERE lesson_id=?',(day,)).fetchone()[0]
        conn.execute('INSERT INTO pronunciation_items(lesson_id,position,category,grapheme,ipa,example_fr,example_ipa,meaning_en,articulation,contrast) VALUES (?,?,?,?,?,?,?,?,?,?)',(day,position,'letter name',letter,ipa,name,ipa,f'letter {letter}','Say the letter name when spelling; its sound inside words can change.',None))
    for day in (1,2):
        conn.execute('UPDATE pronunciation_items SET position=-position WHERE lesson_id=?',(day,))
        letters=conn.execute('SELECT id FROM pronunciation_items WHERE lesson_id=? ORDER BY grapheme',(day,)).fetchall()
        for pos,(item_id,) in enumerate(letters,1):
            conn.execute('UPDATE pronunciation_items SET position=? WHERE id=?',(pos,item_id))
    for day,content in A0.items():
        conn.execute('UPDATE lessons SET objective=?,estimated_minutes=? WHERE id=?',(content['goal'],30 if day not in (7,14) else 40,day))
        conn.execute('DELETE FROM lesson_blocks WHERE lesson_id=?',(day,))
        pos=1
        for title,explanation,example in content['steps']:
            block={'heading':title,'text':explanation,'example':example}
            conn.execute('INSERT INTO lesson_blocks(lesson_id,position,block_type,content_json) VALUES (?,?,?,?)',(day,pos,'explanation',json.dumps(block,ensure_ascii=False)))
            pos+=1
        conn.execute('INSERT INTO lesson_blocks(lesson_id,position,block_type,content_json) VALUES (?,?,?,?)',(day,pos,'production',json.dumps({'heading':'Say it and write it','instruction':content['practice'],'model':conn.execute('SELECT example_fr FROM lessons WHERE id=?',(day,)).fetchone()[0] or ''},ensure_ascii=False)))
        conn.execute('DELETE FROM exercise_choices WHERE exercise_id IN (SELECT id FROM exercises WHERE lesson_id=?)',(day,))
        conn.execute('DELETE FROM exercises WHERE lesson_id=?',(day,))
        for position,(prompt,correct,wrong1,wrong2,reason) in enumerate(content['checks'],1):
            cur=conn.execute('INSERT INTO exercises(lesson_id,kind,prompt,answer,explanation,auto_gradable,position) VALUES (?,?,?,?,?,?,?)',(day,'choice',prompt,correct,reason,1,position))
            opts=[correct,wrong1,wrong2]
            offset=(day+position)%3
            opts=opts[offset:]+opts[:offset]
            for idx,option in enumerate(opts,1):
                conn.execute('INSERT INTO exercise_choices VALUES (?,?,?,?)',(cur.lastrowid,idx,option,int(option==correct)))
        conn.execute('INSERT INTO exercises(lesson_id,kind,prompt,answer,explanation,auto_gradable,position) VALUES (?,?,?,?,?,?,?)',(day,'production',content['practice'],None,'Self-check with the lesson steps. Pronunciation needs an audio model or a trained assessor; no automatic score is assigned.',0,len(content['checks'])+1))
        conn.execute('DELETE FROM flashcards WHERE lesson_id=? AND lexeme_id IS NULL',(day,))
        for item in PRONUNCIATION.get(day,[]):
            category,grapheme,ipa,word,word_ipa,meaning,articulation,contrast=item
            for direction,front,back in [('fr_en',word,f'{word_ipa} · {meaning}'),('en_fr',meaning,f'{word} {word_ipa}')]:
                conn.execute('INSERT INTO flashcards(lesson_id,front,back,direction,tags_json) VALUES (?,?,?,?,?)',(day,front,back,direction,json.dumps(['A0','pronunciation',category],ensure_ascii=False)))
    # Every later day gets a distinct retrieval, noticing and transfer path.
    # This supports a structured app flow while subsequent editorial expansion continues.
    for row in conn.execute('SELECT l.id,l.title,l.objective,l.example_fr,l.example_en,u.title,u.level_code FROM lessons l JOIN units u ON u.id=l.unit_id WHERE l.id>14').fetchall():
        day,title,objective,fr,en,unit,level=row
        if fr:
            steps=[
              ('Recall','Before reading, name yesterday’s key expression or rule from memory. Revisit a missed card if recall fails.',None),
              ('Notice',f'Focus on {title.lower()}. Read the model and identify the part that expresses today’s meaning.',fr),
              ('Meaning',f'Connect the French model to its meaning: {en}. Notice who acts, when it happens and which words carry the meaning.',en),
              ('Change one detail',f'Keep the pattern from {fr} and change one appropriate detail for your own context. Check agreement, tense and word order before speaking.',None),
              ('Independent use',f'Produce a fresh example about {unit.lower()} without looking at the model. Compare it with the studied structure; multiple answers may be valid.',None)]
        else:
            steps=[('Retrieve','Recall this unit’s six new expressions without looking. Mark any that need another pass.',None),('Contrast','Explain the difference between two similar patterns from this unit, using your own examples.',None),('Apply',f'Use material from {unit.lower()} in a short realistic exchange or paragraph.',None)]
        position=4 if fr else 2
        for heading,text,example in steps:
            conn.execute('INSERT INTO lesson_blocks(lesson_id,position,block_type,content_json) VALUES (?,?,?,?)',(day,position,'explanation',json.dumps({'heading':heading,'text':text,'example':example},ensure_ascii=False)))
            position+=1
        if fr:
            conn.execute('INSERT INTO exercises(lesson_id,kind,prompt,answer,explanation,auto_gradable,position) VALUES (?,?,?,?,?,?,?)',(day,'production',f'Change one meaningful detail of “{fr}” and explain what changed in English.',None,'Compare the new meaning and form with the lesson model; valid alternatives need review.',0,3))
            conn.execute('INSERT INTO exercises(lesson_id,kind,prompt,answer,explanation,auto_gradable,position) VALUES (?,?,?,?,?,?,?)',(day,'production',f'In a new context, use today’s focus “{title}” to produce an original French utterance.',None,'Self-check the intended meaning, word order, forms and pronunciation; no automatic correctness claim.',0,4))
        else:
            task,rubric=REVIEW_TASKS[level]
            scenario=f'Topic: {unit}. {task}'
            conn.execute('UPDATE lesson_blocks SET content_json=? WHERE lesson_id=? AND block_type="review"',(json.dumps({'heading':'Unit performance task','scenario':scenario,'rubric':rubric,'steps':['Retrieve the six focus patterns.','Complete the objective checkpoint.','Record or write the original response.','Use the rubric to self-assess and revisit weak points.'],'pass_threshold':0.8,'certification':False},ensure_ascii=False),day))
            conn.execute('UPDATE exercises SET prompt=?,explanation=? WHERE lesson_id=? AND kind="production"',(scenario,f'Self-check: {rubric}. Fluency or CEFR attainment cannot be awarded by this seed.',day))
