from db.models import Lecture, Query, ImageUpload


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


def create_query_text_for_image(query: Query, upload: ImageUpload):
    return f'''
Answer the following prompt about an assignment. If the answer contains math,
wrap all equations and expressions in latex.

Assignment Description:
{upload.description_en}

Assignment Content:
{upload.text_content}

Prompt:
{query.query_string}

Answer:
'''.strip()
