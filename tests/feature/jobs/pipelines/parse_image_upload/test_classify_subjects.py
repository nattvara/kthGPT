from jobs.pipelines.parse_image_upload import (
    classify_subjects
)


def get_mocked_classifier(labels, err=None):
    class ClassifierMock:
        def __init__(self) -> None:
            pass

        def classify(self, text: str) -> list:
            if err:
                raise err
            return labels

    return ClassifierMock()


def test_classify_subjects_job_creates_imageupload_subjects(mocker, image_upload):
    labels = ['foo', 'bar']
    mocker.patch(
        'classifiers.SubjectClassifier.create_classifier_for',
        return_value=get_mocked_classifier(labels)
    )

    classify_subjects.job(image_upload.public_id)
    image_upload.refresh()

    assert len(image_upload.subjects_list()) == 2
    for label in labels:
        assert label in image_upload.subjects_list()


def test_classify_subjects_saves_progress(mocker, image_upload):
    labels = ['foo', 'bar']
    mocker.patch(
        'classifiers.SubjectClassifier.create_classifier_for',
        return_value=get_mocked_classifier(labels)
    )

    classify_subjects.job(image_upload.public_id)
    image_upload.refresh()

    assert image_upload.classify_subjects_ok is True


def test_create_title_job_saves_failure_reason_on_error(mocker, image_upload):
    labels = ['foo', 'bar']
    err = ValueError('bang!')
    mocker.patch(
        'classifiers.SubjectClassifier.create_classifier_for',
        return_value=get_mocked_classifier(labels, err)
    )

    try:
        classify_subjects.job(image_upload.public_id)
    except Exception:
        pass

    image_upload.refresh()

    assert image_upload.classify_subjects_ok is False
    assert image_upload.classify_subjects_failure_reason == 'bang!'
