from db.models import Lecture, Query, ImageUpload, ImageQuestion


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


def describe_text_content_in_image_english(upload: ImageUpload) -> str:
    return f'''
Consider the content of an assignment captured from an image. Describe the assignment and
what one needs to know to complete the assignment.

Assignment:
{upload.text_content}

Description:
'''.strip()


def describe_text_content_in_image_swedish(upload: ImageUpload) -> str:
    return f'''
Beskriv följande uppgift och vad man behöver kunna för att lösa uppgiften.

Uppgift:
{upload.text_content}

Beskrivning:
'''.strip()


def create_search_query_for_upload_english(upload: ImageUpload) -> str:
    return f'''
Consider the following assignment. To find the answer to this assignment, what would should I google for? Try to use keywords specific for the given theory in addition to specifics of the assignment. Answer
with 5 queries in a list where each entry is separated by a newline without any numbers or bullets.

Description of assignment:
{upload.description_en}

Assignment:
{upload.text_content}

Queries:
'''.strip()


def create_search_query_for_upload_swedish(upload: ImageUpload) -> str:
    return f'''
Vad ska jag googla på för att hitta svaret på denna fråga? Försök att använda nyckelord som är specifika för den givna teorin utöver uppgiftsspecifika sökord. Svara med 5 sökfraser i en lista där varje fråga separeras av en ny rad utan några siffror eller punkter i början på varje rad.

Beskrivning av uppgiften:
{upload.description_sv}

Uppgift:
{upload.text_content}

Frågor:
'''.strip()


def create_prompt_to_answer_question_about_hit(lecture: Lecture, image: ImageUpload, question: ImageQuestion) -> str:
    return f'''
Explain where in the lecture transcript the answer to the given question can be found. Respond using the specified format, use only the specified html tags. Use no more than 50 words per relevant section.

Lecture transcript:
{lecture.summary_text()}

Assignment:
{image.text_content}

Questions:
{question.query_string}

Format to use:
<strong>xx:xx:xx - xx:xx:xx</strong> xxx \n

Relevant segments and answer to each:
'''.strip()


def create_prompt_to_explain_hit_relevance(lecture: Lecture, image: ImageUpload, question: ImageQuestion) -> str:
    return f'''
Answer why this lecture is relevant to the following question. Be brief, use less than 20 words.

Lecture transcript:
{lecture.summary_text()}

Assignment:
{image.text_content}

Questions:
{question.query_string}

Relevance:
'''.strip()
