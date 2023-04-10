import pytest

from jobs.tasks.lecture import classify_subjects


def test_classification_can_approve_video(mocker, make_mocked_classifier, analysed_lecture):
    labels = ['some label', 'some other label']
    mocker.patch(
        'classifiers.SubjectClassifier.create_classifier_for',
        return_value=make_mocked_classifier(labels)
    )

    # Classify the video
    classify_subjects.job(analysed_lecture.public_id, analysed_lecture.language)
    analysed_lecture.refresh()

    assert len(analysed_lecture.subjects_list()) == 2
    for label in labels:
        assert label in analysed_lecture.subjects_list()


def test_lecture_cannot_be_classified_without_description(analysed_lecture):
    analysed_lecture.description = None
    analysed_lecture.save()

    with pytest.raises(
        ValueError,
        match='cannot classify the subjects of a lecture without description'
    ):
        classify_subjects.job(
            analysed_lecture.public_id,
            analysed_lecture.language
        )
