from db.models import Lecture, ImageUpload, ImageQuestion


def create_search_query_for_upload_english(upload: ImageUpload) -> str:
    return f'''
Consider the following assignment. To find the answer to this assignment, what would should I google for?
Try to use keywords specific for the given theory in addition to specifics of the assignment. Answer
with 5 queries in a list where each entry is separated by a newline without any numbers or bullets.

Description of assignment:
{upload.description_en}

Assignment:
{upload.text_content}

Queries:
'''.strip()


def create_search_query_for_upload_swedish(upload: ImageUpload) -> str:
    return f'''
Vad ska jag googla på för att hitta svaret på denna fråga? Försök att använda nyckelord som är specifika för
den givna teorin utöver uppgiftsspecifika sökord. Svara med 5 sökfraser i en lista där varje fråga separeras
av en ny rad utan några siffror eller punkter i början på varje rad.

Beskrivning av uppgiften:
{upload.description_sv}

Uppgift:
{upload.text_content}

Frågor:
'''.strip()


def create_prompt_to_answer_question_about_hit(lecture: Lecture, image: ImageUpload, question: ImageQuestion) -> str:
    return f'''
Explain where in the lecture transcript the answer to the given question can be found. Respond using the
specified format, use only the specified html tags. Use no more than 50 words per relevant section.

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
