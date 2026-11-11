"""Original, reference-informed weekly skill practice. No source PDFs are bundled."""

def P(unit,title,text,summary,questions,dialogue,dialogue_questions,expressions,writing,speaking,grammar):
    return dict(unit=unit,title=title,text=text.strip(),summary=summary,questions=questions,
                dialogue=dialogue,dialogue_questions=dialogue_questions,expressions=expressions,
                writing=writing,speaking=speaking,grammar=grammar)
