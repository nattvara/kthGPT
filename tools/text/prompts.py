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
