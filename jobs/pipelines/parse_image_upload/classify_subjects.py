from classifiers import SubjectClassifier
from db.crud import (
    get_image_upload_by_public_id
)


def job(image_id: str):
    upload = get_image_upload_by_public_id(image_id)
    if upload is None:
        raise ValueError(f'image {image_id} was not found')

    try:
        classifier = SubjectClassifier.create_classifier_for(
            'assignment',
            priority=SubjectClassifier.Priority.HIGH,
            upload=upload,
        )
        labels = classifier.classify(upload.description_en)

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
