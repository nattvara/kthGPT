from db.models import ImageUpload


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


def create_title_from_assignment(upload: ImageUpload) -> str:
    return f'''
Consider the content of an assignment captured from an image. Create a title for the assignment.

Assignment:
{upload.text_content}

Title:
'''.strip()
