
CATEGORY_RECORDED_LECTURE = 'Recorded Lecture'


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
