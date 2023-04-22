from typing import List


def create_classification_prompt_for_subjects(
    what_to_classify: str,
    number_of_labels: int,
    labels: List[str],
    text_to_classify: str,
):
    subjects_str = ''
    for label in labels:
        subjects_str += label + '\n'

    return f'''
Consider the following {what_to_classify.lower()}, and the following list of subjects. Select
which {number_of_labels} subjects the assignment belongs to. Decision should have one subject per line.

{what_to_classify.title()}:
{text_to_classify}

Subjects:
{subjects_str}

Decision:
'''.strip()


def create_validation_prompt_for_subjects(
    what_to_classify: str,
    labels: List[str],
    text_to_classify: str,
):
    subjects_str = ''
    for label in labels:
        subjects_str += label + '\n'

    return f'''
Select which of the following subjects are good classifications of the {what_to_classify.lower()}. Decision
must have one subject per line.

Subjects:
{subjects_str}

{what_to_classify.title()}:
{text_to_classify}

Decision:
'''.strip()
