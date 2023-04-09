from typing import List


def create_classification_prompt_for_subjects(
    what_to_classify: str,
    number_of_labels: int,
    labels: List[str],
):
    return f'''
Consider the following {what_to_classify.lower()}, and the following list of subjects. Select the {number_of_labels} most applicable subjects. Responds with each label on a separate line.

{what_to_classify.title()}:

Subjects:
{', '.join(labels)}

Decision:
'''.strip()
