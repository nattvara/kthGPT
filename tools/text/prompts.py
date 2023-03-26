from db.models import Lecture, Query, ImageUpload


CATEGORY_RECORDED_LECTURE = 'Recorded Lecture'


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


def create_query_text_english(query: Query, lecture: Lecture):
    return f'''
Answer the following prompt about a recorded lecture.

Lecture:
{lecture.summary_text()}

Prompt:
{query.query_string}

Answer:
'''.strip()


def create_query_text_swedish(query: Query, lecture: Lecture):
    return f'''
Svara på följande fråga om en inspelad föreläsning.

Innehållet i föreläsningen:
{lecture.summary_text()}

Fråga:
{query.query_string}

Svar:
'''.strip()


def create_text_to_decide_if_video_is_appropriate_english(text):
    categories = [
        'Entertainment',
        'Infotainment',
        'Reviews',
        'Sports',
        'ASMR',
        'Compilations',
        'Gaming',
        'Journalism',
        'Reviews',
        CATEGORY_RECORDED_LECTURE,
    ]

    return f'''
Decide whether a video is one of the following categories {', '.join(categories)}.

Video Transcript:
{text}

Decision:
'''.strip()


def create_text_to_decide_if_video_is_appropriate_swedish(text):
    categories = [
        'Entertainment',
        'Infotainment',
        'Reviews',
        'Sports',
        'ASMR',
        'Compilations',
        'Gaming',
        'Journalism',
        'Reviews',
        CATEGORY_RECORDED_LECTURE,
    ]

    return f'''
Besluta vilken av dessa engelska kategorier denna video tillhör {', '.join(categories)}.

Videons innehåll:
{text}

Beslut:
'''.strip()


def describe_text_content_in_image(upload: ImageUpload) -> str:
    return f'''
Consider the content of an assignment captured from an image. Describe the assignment and what one needs to know to complete the assignment.

Assignment:
{upload.text_content}

Description:
'''.strip()
