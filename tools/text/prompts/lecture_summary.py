from db.models import Lecture


def create_text_to_summarise_chunk_english(summary, chunk, include_summary: bool):
    summary_string = ''
    if include_summary:
        summary_string = f'''
The lecture has previously covered:
{summary.summarise()}
'''

    return f'''
Summarize the transcript of a subsection of the lecture, use no more than {summary.summary_size} words.
{summary_string}
Transcript:
{chunk.transcript}

Transcript summary:
'''.strip()


def create_text_to_summarise_chunk_swedish(summary, chunk, include_summary: bool):
    summary_string = ''
    if include_summary:
        summary_string = f'''
Föreläsningens innehåll hittills:
{summary.summarise()}
'''

    return f'''
Sammanfatta nästa del av föreläsningen, använd max {summary.summary_size} ord.
{summary_string}

Nästa del:
{chunk.transcript}

Sammanfattning:
'''.strip()


def create_text_to_summarise_summary_english(summary):
    return f'''
Summarize the contents of this lecture into no more than 250 words.

The lecture is about:
{summary.current_summary()}

Summary:
'''.strip()


def create_text_to_summarise_summary_swedish(summary):
    return f'''
Sammanfatta innehållet i den här föreläsningen, använd max 250 ord.

Föreläsningen handlar om:
{summary.current_summary()}

Sammanfattning:
'''.strip()


def create_description_prompt(lecture: Lecture):
    # The word 'summary' seems to have a better effect than 'description'
    return f'''
Summarize the contents of this lecture into no more than 400 words. The must
be in english. The summary should include important keywords.

The lecture is about:
{lecture.summary_text()}

Summary:
'''.strip()
