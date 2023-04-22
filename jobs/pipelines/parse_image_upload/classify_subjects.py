from classifiers import SubjectMultipassClassifier
from db.crud import (
    get_image_upload_by_public_id
)


def job(image_id: str):
    upload = get_image_upload_by_public_id(image_id)
    if upload is None:
        raise ValueError(f'image {image_id} was not found')

    try:
        classifier = SubjectMultipassClassifier.create_classifier_for(
            'question',
            priority=SubjectMultipassClassifier.Priority.HIGH,
            upload=upload,
            samples=3,
        )
        text = f'''
{upload.text_content}
{upload.description_en}
        '''.strip()
        labels = classifier.classify(text)

        for label in labels:
            upload.add_subject(label)

        upload.classify_subjects_ok = True
        upload.classify_subjects_failure_reason = None

        upload.save()
    except Exception as e:
        upload.classify_subjects_ok = False
        upload.classify_subjects_failure_reason = str(e)
        upload.save()
        raise e
