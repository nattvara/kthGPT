from db.models import Lecture, Query


def create_text_to_summarise_chunk(summary, chunk, include_summary: bool):
    summary_string = ''
    if include_summary:
        summary_string = f'''
The lecture has previously covered:
{summary.summarise()}
'''

    return f'''
Summarize the transcript of a subsection of a lecture, use no more than {summary.summary_size} words.
{summary_string}
Transcript:
{chunk.transcript}

Transcript summary:
'''.strip()


def create_text_to_summarise_summary(summary):
    return f'''
Summarize the contents of this lecture into no more than 250 words.

The lecture is about:
{summary.current_summary()}

Summary:
'''.strip()


def create_query_text(query: Query, lecture: Lecture):
    return f'''
Answer the following prompt about a recorded lecture.

Lecture:
{lecture.summary_text()}

Prompt:
{query.query_string}

Answer:
'''.strip()
