"""Curated thematic headwords. Articles are taught with gender; IPA is added only when vetted."""
import json

# Unit sequence -> French~English~part of speech~gender; keep words distinct from phrase cards.
THEMES={
3:'je~I~pronoun~|tu~you (familiar singular)~pronoun~|il~he~pronoun~|elle~she~pronoun~|nous~we~pronoun~|vous~you (formal or plural)~pronoun~|ils~they (masculine or mixed)~pronoun~|elles~they (feminine)~pronoun~',
4:'un~a/an masculine~article~|une~a/an feminine~article~|le~the masculine~article~|la~the feminine~article~|les~the plural~article~|l’~the before vowel~article~|stylo~pen~noun~m|chaise~chair~noun~f|fenêtre~window~noun~f|porte~door~noun~f|appartement~apartment~noun~m|bureau~desk or office~noun~m',
5:'parler~speak~verb~|aimer~like or love~verb~|habiter~live~verb~|regarder~watch or look at~verb~|écouter~listen to~verb~|travailler~work~verb~|étudier~study~verb~|jouer~play~verb~|chanter~sing~verb~|danser~dance~verb~',
6:'qui~who~interrogative~|quoi~what~interrogative~|que~what or that~interrogative~|où~where~interrogative~|quand~when~interrogative~|pourquoi~why~interrogative~|comment~how~interrogative~|combien~how many or how much~interrogative~',
7:'lundi~Monday~noun~m|mardi~Tuesday~noun~m|mercredi~Wednesday~noun~m|jeudi~Thursday~noun~m|vendredi~Friday~noun~m|samedi~Saturday~noun~m|dimanche~Sunday~noun~m|minute~minute~noun~f|mois~month~noun~m|rendez-vous~appointment~noun~m',
8:'grand-père~grandfather~noun~m|grand-mère~grandmother~noun~f|parent~parent~noun~m|cousin~male cousin~noun~m|cousine~female cousin~noun~f|fils~son~noun~m|fille~daughter or girl~noun~f|mari~husband~noun~m|épouse~wife~noun~f|mon~my masculine~determiner~|ma~my feminine~determiner~|mes~my plural~determiner~',
9:'rouge~red~adjective~|bleu~blue~adjective~|vert~green~adjective~|noir~black~adjective~|blanc~white~adjective~|jaune~yellow~adjective~|vieux~old~adjective~|long~long~adjective~|court~short~adjective~|cher~expensive~adjective~',
10:'pomme~apple~noun~f|orange~orange~noun~f|banane~banana~noun~f|fromage~cheese~noun~m|riz~rice~noun~m|lait~milk~noun~m|sucre~sugar~noun~m|sel~salt~noun~m|poisson~fish~noun~m|viande~meat~noun~f|légume~vegetable~noun~m',
11:'pharmacie~pharmacy~noun~f|banque~bank~noun~f|poste~post office~noun~f|marché~market~noun~m|magasin~shop~noun~m|bibliothèque~library~noun~f|musée~museum~noun~m|parc~park~noun~m|pont~bridge~noun~m|carrefour~intersection~noun~m',
12:'cher~dear or expensive~adjective~|prix~price~noun~m|taille~size~noun~f|caisse~checkout~noun~f|monnaie~change or currency~noun~f|carte~card~noun~f|espèces~cash~noun~f|client~customer~noun~m|cliente~customer~noun~f|commande~order~noun~f',
13:'santé~health~noun~f|médecin~doctor~noun~m|douleur~pain~noun~f|tête~head~noun~f|main~hand~noun~f|pied~foot~noun~m|bras~arm~noun~m|fièvre~fever~noun~f|fatigue~tiredness~noun~f|malade~ill~adjective~',
14:'voyage~journey~noun~m|valise~suitcase~noun~f|aéroport~airport~noun~m|avion~plane~noun~m|bus~bus~noun~m|métro~metro~noun~m|retard~delay~noun~m|départ~departure~noun~m|arrivée~arrival~noun~f|quai~platform~noun~m',
15:'passé~past~noun~m|souvenir~memory~noun~m|histoire~story or history~noun~f|vacances~holidays~noun~f|photo~photo~noun~f|découverte~discovery~noun~f|rencontre~meeting~noun~f|événement~event~noun~m',
16:'depuis~since or for (continuing)~preposition~|pendant~during or for (bounded)~preposition~|autrefois~formerly~adverb~|déjà~already~adverb~|encore~still or again~adverb~|ensuite~then~adverb~|soudain~suddenly~adverb~|bientôt~soon~adverb~',
17:'projet~project~noun~m|objectif~goal~noun~m|prévision~forecast~noun~f|plan~plan~noun~m|avenir~future~noun~m|possibilité~possibility~noun~f|intention~intention~noun~f|étape~step~noun~f',
18:'formation~training~noun~f|entreprise~company~noun~f|collègue~colleague~noun~m|réunion~meeting~noun~f|dossier~file~noun~m|délai~deadline~noun~m|tâche~task~noun~f|responsable~manager~noun~m|équipe~team~noun~f',
19:'quartier~neighborhood~noun~m|logement~housing~noun~m|loyer~rent~noun~m|voisin~neighbor~noun~m|voisine~neighbor~noun~f|immeuble~building~noun~m|ascenseur~elevator~noun~m|étage~floor~noun~m',
20:'émission~program~noun~f|article~article~noun~m|journal~newspaper~noun~m|information~information~noun~f|actualités~news~noun~f|entretien~interview~noun~m|reportage~report~noun~m|témoignage~testimony~noun~m',
21:'avantage~advantage~noun~m|inconvénient~disadvantage~noun~m|cause~cause~noun~f|conséquence~consequence~noun~f|exemple~example~noun~m|raison~reason~noun~f|choix~choice~noun~m|préférence~preference~noun~f',
23:'environnement~environment~noun~m|déchet~waste item~noun~m|énergie~energy~noun~f|climat~climate~noun~m|ressource~resource~noun~f|pollution~pollution~noun~f|durable~sustainable~adjective~|recyclage~recycling~noun~m',
25:'hypothèse~hypothesis~noun~f|condition~condition~noun~f|probabilité~probability~noun~f|certitude~certainty~noun~f|doute~doubt~noun~m|supposition~assumption~noun~f|éventuel~possible~adjective~',
27:'débat~debate~noun~m|enjeu~issue or stake~noun~m|thèse~thesis~noun~f|réfutation~rebuttal~noun~f|nuance~nuance~noun~f|concession~concession~noun~f|contradiction~contradiction~noun~f',
30:'citoyen~citizen~noun~m|citoyenne~citizen~noun~f|institution~institution~noun~f|politique~policy or politics~noun~f|réforme~reform~noun~f|mesure~measure~noun~f|droit~right or law~noun~m|devoir~duty~noun~m',
35:'synthèse~synthesis~noun~f|résumé~summary~noun~m|interprétation~interpretation~noun~f|perspective~perspective~noun~f|cadre~framework~noun~m|limite~limit~noun~f|portée~scope~noun~f',
39:'ironie~irony~noun~f|sous-entendu~implication~noun~m|allusion~allusion~noun~f|ambiguïté~ambiguity~noun~f|implicite~implicit~adjective~|explicite~explicit~adjective~|registre~register~noun~m',
45:'rhétorique~rhetoric~noun~f|argumentation~argumentation~noun~f|contre-argument~counterargument~noun~m|prémisse~premise~noun~f|conclusion~conclusion~noun~f|cohérence~coherence~noun~f|pertinence~relevance~noun~f',
51:'subtilité~subtlety~noun~f|connotation~connotation~noun~f|équivoque~ambiguity~noun~f|paradoxe~paradox~noun~m|litote~understatement~noun~f|métaphore~metaphor~noun~f|ellipse~ellipsis~noun~f',
56:'plaidoyer~plea or advocacy~noun~m|diplomatie~diplomacy~noun~f|compromis~compromise~noun~m|arbitrage~arbitration~noun~m|médiation~mediation~noun~f|précision~precision~noun~f|réserve~reservation or caution~noun~f',
}

def apply(conn):
    total=0
    for week,records in THEMES.items():
        level=conn.execute('SELECT level_code FROM units WHERE id=?',(week,)).fetchone()[0]
        for index,item in enumerate(records.split('|')):
            if not item: continue
            french,english,pos,gender=item.split('~')
            lesson=(week-1)*7+1+(index%6)
            cur=conn.execute('INSERT OR IGNORE INTO lexemes(french,english,part_of_speech,gender,level_code) VALUES (?,?,?,?,?)',(french,english,pos,gender or None,level))
            if not cur.rowcount: continue
            lexeme=cur.lastrowid
            conn.execute('INSERT INTO lesson_lexemes VALUES (?,?)',(lesson,lexeme))
            for direction,front,back in [('fr_en',french,english),('en_fr',english,french)]:
                conn.execute('INSERT INTO flashcards(lesson_id,lexeme_id,front,back,direction,tags_json) VALUES (?,?,?,?,?,?)',(lesson,lexeme,front,back,direction,json.dumps(['thematic_vocabulary',level])))
            total+=1
    return total
