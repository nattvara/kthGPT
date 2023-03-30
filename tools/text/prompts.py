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


def describe_text_content_in_image(upload: ImageUpload) -> str:
    return f'''
Consider the content of an assignment captured from an image. Describe the assignment and
what one needs to know to complete the assignment.

Assignment:
{upload.text_content}

Description:
'''.strip()


def create_search_query_for_upload_english(upload: ImageUpload) -> str:
    return f'''
Consider the following assignment. To find the answer to this assignment, what would should I search for? Answer
with 5 queries in a list where each entry is separated by a newline without any numbers or bullets.

Assignment:
{upload.text_content}

Queries:
'''.strip()


def create_search_query_for_upload_swedish(upload: ImageUpload) -> str:
    return f'''
Consider the following assignments. To find the answer to this assignment, what would should I search for? Answer
with 5 queries in a list where each entry is separated by a newline without any numbers or bullets. The search
queries must be in swedish.

Assignment:
{upload.text_content}

Queries:
'''.strip()


def create_prompt_to_operationalise_question(image: ImageUpload, question: ImageQuestion) -> str:
    return f'''
Consider an assignment and a prompt from the user. Given that I have the transcript of a relevant lecture. What should I ask about that transcript to best reply to the prompt? And specifically how it relates to this lecture. Respond with two questions in a bulleted list.

Assignment:
{image.text_content}

Prompt:
{question.query_string}

Questions:
'''.strip()


def create_prompt_to_answer_question_about_hit(lecture: Lecture, image: ImageUpload, question: ImageQuestion) -> str:
    return f'''
Answer the following question using the specified format, use the html tags. If the lecture answers the question, use references to the transcript. Use no more than 50 words per relevant section.

Lecture transcript:
{lecture.summary_text()}

Assignment:
{image.text_content}

Questions:
{question.operationalised_query}

Format to use:
<strong>xx:xx:xx - xx:xx:xx</strong> [answer] \n

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
{question.operationalised_query}

Relevance:
'''.strip()
