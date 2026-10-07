# Vocabulary data provenance

The `conversation_words.tsv` IPA column uses French pronunciation data from
[open-dict-data/ipa-dict](https://github.com/open-dict-data/ipa-dict), compiled
from French Wiktionary contributors under Creative Commons Attribution
ShareAlike. This project's selection and presentation change the source data.
See the upstream repository for its [license and attribution](https://github.com/open-dict-data/ipa-dict#license).

The French word selection and short glosses were informed by several common
vocabulary references, including [exekis/lang-1000](https://github.com/exekis/lang-1000).
No example sentences or recordings from that repository are included.
Its repository did not declare a data license when consulted. The English
glosses are brief factual translations; review provenance before commercial
redistribution of the complete selected list.

The 50 present-tense paradigms in `conjugation_overrides.tsv` derive from
[alexedmon1/french-daily](https://github.com/alexedmon1/french-daily),
`conjugation_data/verbs.json`. Its MIT license follows:

> MIT License
>
> Copyright (c) 2025 Alex D. Edmondson
>
> Permission is hereby granted, free of charge, to any person obtaining a copy
> of this software and associated documentation files (the "Software"), to deal
> in the Software without restriction, including without limitation the rights
> to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
> copies of the Software, and to permit persons to whom the Software is
> furnished to do so, subject to the following conditions:
>
> The above copyright notice and this permission notice shall be included in
> all copies or substantial portions of the Software.
>
> THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
> IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
> FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
> AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
> LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
> OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
> SOFTWARE.

## Second vocabulary bank (ranks 1,001–2,000)

- Lemma, part of speech, available noun gender, and approximate frequency
  ordering: [wordhoard French sample](https://github.com/natema/wordhoard/blob/main/samples/fr.csv),
  a CC BY-SA 4.0 dataset. Credit wordhoard, Wiktionary contributors via
  kaikki.org, OpenSubtitles frequency data via FrequencyWords, and spaCy as
  described in its [NOTICE](https://github.com/natema/wordhoard/blob/main/NOTICE.md).
  Additional candidates were selected using
  [FrequencyWords French subtitles list](https://github.com/hermitdave/FrequencyWords/blob/master/content/2018/fr/fr_50k.txt).
  The two rank systems are estimates and are not directly comparable.
- Short English glosses and part-of-speech cross-checks:
  [French Wiktionary bilingual extraction](https://github.com/pquentin/wiktionary-translations),
  based on French Wiktionary contributions under CC BY-SA. A gloss selects one
  sense and is not a complete dictionary definition.
- IPA: [ipa-dict French (France)](https://github.com/open-dict-data/ipa-dict/blob/master/data/fr_FR.txt).
  Broad citation forms can vary by region or sentence context.
- French–English usage examples: text sentences from
  [Tatoeba](https://tatoeba.org), via a
  [bilingual text mirror](https://github.com/desmondyeoh/data-eng-fra).
  Tatoeba contributors release text under
  [CC BY 2.0 France](https://tatoeba.org/en/terms_of_use).
  The pairs were selected and aligned to the headwords here; their source
  authors and IDs were not preserved by the mirror. The rows are labeled
  `corpus_unreviewed`, because automated sense matching can still pick an
  awkward example or translation. No recordings are redistributed.

The new vocabulary subset combines share-alike word data with attributed
Tatoeba sentences. Preserve this notice and the relevant licenses in any
redistribution of the database or JSON export. Content selection, glosses,
examples, and CEFR placement still need educator review.
