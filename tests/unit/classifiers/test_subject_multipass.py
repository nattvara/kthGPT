from unittest.mock import call

from classifiers import SubjectMultipassClassifier

TEXT_STRING = '''
some text mentioning a bunch of math jargon

The eigenvector corresponding to the maximum eigenvalue of the covariance matrix
facilitates dimensionality reduction in principal component analysis,
effectively projecting the data onto a lower-dimensional subspace.
Meanwhile, the Riemann zeta function, analytically continued to
the complex plane, yields nontrivial zeros that provide
insights into the distribution of prime numbers
via the Prime Number Theorem.
'''


def test_subject_multipass_classifier_can_be_created():
    classifier_1 = SubjectMultipassClassifier.create_classifier_for('lecture')
    classifier_2 = SubjectMultipassClassifier.create_classifier_for('assignment')

    assert classifier_1.what == 'lecture'
    assert classifier_2.what == 'assignment'


def test_classification_use_subject_classifier(mocker):
    mocker.patch('tools.text.ai.gpt3')

    return_1 = ['Mathematics', 'Engineering Sciences']
    subject_mock = mocker.patch('classifiers.subject.SubjectClassifier.classify', return_value=return_1)

    classifier = SubjectMultipassClassifier.create_classifier_for('lecture')

    result = classifier.classify(TEXT_STRING)

    assert result == ['Mathematics', 'Engineering Sciences']
    assert subject_mock.call_count == 1


def test_classification_can_sample_multiple_times(mocker):
    mocker.patch('tools.text.ai.gpt3')

    subject_mock = mocker.patch('classifiers.subject.SubjectClassifier.classify', return_value=['foo'])
    classifier = SubjectMultipassClassifier.create_classifier_for(
        'lecture',
        samples=10
    )

    classifier.classify(TEXT_STRING)

    assert subject_mock.call_count == 10 + 1  # one extra for the validation pass


def test_validation_pass_is_used_with_sampled_subjects(mocker):
    return_1 = ['foo', 'bar']
    return_2 = ['foo', 'baz']
    return_3 = ['bat']
    return_4 = ['foo']  # return of the final pass

    mocker.patch('classifiers.subject.SubjectClassifier.classify', side_effect=[
        return_1,
        return_2,
        return_3,
        return_4,
    ])
    override_labels_mock = mocker.patch('classifiers.subject.SubjectClassifier.override_labels')

    classifier = SubjectMultipassClassifier.create_classifier_for(
        'lecture',
        samples=3
    )

    result = classifier.classify(TEXT_STRING)

    assert override_labels_mock.call_count == 1
    assert override_labels_mock.mock_calls[0] == call(
        ['foo', 'bar', 'baz', 'bat']
    )
    assert result == ['foo']


def test_last_pass_is_using_a_custom_validation_prompt(mocker):
    classify_mock = mocker.patch('classifiers.subject.SubjectClassifier.classify', return_value=['foo'])

    classifier = SubjectMultipassClassifier.create_classifier_for(
        'lecture',
        samples=3
    )

    classifier.classify(TEXT_STRING)

    assert classify_mock.call_count == 4
    assert list(classify_mock.mock_calls)[-1] == call(
        TEXT_STRING,
        0,
        validation_prompt=True,
    )


def test_last_pass_will_be_rerun_if_result_is_empty(mocker):
    return_1 = ['foo']
    return_2 = ['foo']
    return_3 = ['foo']

    # final passes
    return_4 = []
    return_5 = ['foo']
    classify_mock = mocker.patch('classifiers.subject.SubjectClassifier.classify', side_effect=[
        return_1,
        return_2,
        return_3,
        return_4,
        return_5,
    ])

    classifier = SubjectMultipassClassifier.create_classifier_for(
        'lecture',
        samples=3
    )

    classifier.classify(TEXT_STRING)

    assert classify_mock.call_count == 5
