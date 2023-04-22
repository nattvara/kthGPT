import logging

from db.crud import get_lecture_by_public_id_and_language
from classifiers.subject_multipass import SubjectMultipassClassifier

# 5 mins
TIMEOUT = 5 * 60


def job(lecture_id: str, language: str):
    logger = logging.getLogger('rq.worker')

    lecture = get_lecture_by_public_id_and_language(lecture_id, language)
    if lecture is None:
        raise ValueError(f'lecture {lecture_id} not found')

    if lecture.description is None:
        raise ValueError('cannot classify the subjects of a lecture without description')

    analysis = lecture.get_last_analysis()

    classifier = SubjectMultipassClassifier.create_classifier_for(
        'lecture',
        priority=SubjectMultipassClassifier.Priority.LOW,
        analysis=analysis,
    )
    labels = classifier.classify(lecture.description)

    for label in labels:
        lecture.add_subject(label)

    lecture.reindex()

    logger.info('done.')
