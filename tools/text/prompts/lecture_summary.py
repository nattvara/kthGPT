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
Consider the contents of this lecture. Create a text that first, summarizes the topics covered, then
another paragraph that explains the content, followed by a paragraph about the broader context about
the content, such as why it is important and in which scientific fields. The text must be in english.

The lecture is about:
{lecture.summary_text()}

Text:
'''.strip()
