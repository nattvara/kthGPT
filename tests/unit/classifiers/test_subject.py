from unittest.mock import call

from classifiers import SubjectClassifier

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


def test_subject_classifier_can_be_created():
    classifier_1 = SubjectClassifier.create_classifier_for('lecture')
    classifier_2 = SubjectClassifier.create_classifier_for('assignment')

    assert classifier_1.what == 'lecture'
    assert classifier_2.what == 'assignment'


def test_classification_can_be_make(mocker):
    gpt_response = '''
Mathematics
Engineering Sciences
'''
    gpt3_mock = mocker.patch('tools.text.ai.gpt3', return_value=gpt_response)

    classifier = SubjectClassifier.create_classifier_for('lecture')

    result = classifier.classify(TEXT_STRING)

    assert result == ['Mathematics', 'Engineering Sciences']
    assert gpt3_mock.call_count == 1


def test_classification_can_have_priority(mocker):
    gpt_response = '''
Mathematics
Engineering Sciences
'''
    gpt3_mock = mocker.patch('tools.text.ai.gpt3', return_value=gpt_response)

    priority = SubjectClassifier.Priority.DEFAULT
    classifier = SubjectClassifier.create_classifier_for('lecture', priority=priority)
    classifier.classify(TEXT_STRING)

    assert gpt3_mock.mock_calls[0] == call(
        classifier.create_prompt(TEXT_STRING),
        time_to_live=60 * 2,
        max_retries=4,
        retry_interval=[
            5,
            15,
            30,
            60,
        ],
        upload_id=None,
        analysis_id=None,
    )

    priority = SubjectClassifier.Priority.HIGH
    classifier = SubjectClassifier.create_classifier_for('lecture', priority=priority)
    classifier.classify(TEXT_STRING)

    assert gpt3_mock.mock_calls[1] == call(
        classifier.create_prompt(TEXT_STRING),
        time_to_live=60,
        max_retries=5,
        retry_interval=[
            5,
            10,
            10,
            10,
            10,
        ],
        upload_id=None,
        analysis_id=None,
    )

    priority = SubjectClassifier.Priority.LOW
    classifier = SubjectClassifier.create_classifier_for('lecture', priority=priority)
    classifier.classify(TEXT_STRING)

    assert gpt3_mock.mock_calls[2] == call(
        classifier.create_prompt(TEXT_STRING),
        time_to_live=60 * 60 * 10,
        max_retries=10,
        retry_interval=[
            10,
            30,
            60,
            2 * 60,
            2 * 60,
            10 * 60,
            30 * 60,
            2 * 60 * 60,
            30 * 60,
            30 * 60,
        ],
        upload_id=None,
        analysis_id=None,
    )


def test_classification_result_only_contains_labels(mocker):
    gpt_response_with_bogus_classes = '''
Mathematics
Foo
Bar
Engineering Sciences
'''

    mocker.patch('tools.text.ai.gpt3', return_value=gpt_response_with_bogus_classes)

    classifier = SubjectClassifier.create_classifier_for('lecture')

    result = classifier.classify(TEXT_STRING)

    assert result == ['Mathematics', 'Engineering Sciences']


def test_classifier_can_ignore_messy_gpt_output(mocker):
    gpt_response = '''
- Mathematics
*Engineering Sciences
-Communication
(Computer Science)
'''

    mocker.patch('tools.text.ai.gpt3', return_value=gpt_response)

    classifier = SubjectClassifier.create_classifier_for('lecture')

    result = classifier.classify(TEXT_STRING)

    assert result == ['Mathematics', 'Engineering Sciences', 'Communication', 'Computer Science']


def test_classifier_can_handle_classes_on_one_line(mocker):
    gpt_response = 'Mathematics, Engineering Sciences'

    mocker.patch('tools.text.ai.gpt3', return_value=gpt_response)

    classifier = SubjectClassifier.create_classifier_for('lecture')

    result = classifier.classify(TEXT_STRING)

    assert result == ['Engineering Sciences', 'Mathematics']


def test_classifier_can_handle_classes_irrespective_of_casing(mocker):
    gpt_response = '''
mathematics
ENGINEERING ScienCES
Communication
'''

    mocker.patch('tools.text.ai.gpt3', return_value=gpt_response)

    classifier = SubjectClassifier.create_classifier_for('lecture')

    result = classifier.classify(TEXT_STRING)

    assert result == ['Mathematics', 'Engineering Sciences', 'Communication']


def test_classification_can_have_upload_attached(mocker, image_upload):
    gpt3_mock = mocker.patch('tools.text.ai.gpt3')

    classifier = SubjectClassifier.create_classifier_for('lecture', upload=image_upload)
    classifier.classify(TEXT_STRING)

    assert gpt3_mock.mock_calls[0] == call(
        classifier.create_prompt(TEXT_STRING),
        time_to_live=60 * 2,
        max_retries=4,
        retry_interval=[
            5,
            15,
            30,
            60,
        ],
        upload_id=image_upload.id,
        analysis_id=None,
    )


def test_classification_can_have_analysis_attached(mocker, analysed_lecture):
    gpt3_mock = mocker.patch('tools.text.ai.gpt3')

    analysis = analysed_lecture.get_last_analysis()

    classifier = SubjectClassifier.create_classifier_for('lecture', analysis=analysis)
    classifier.classify(TEXT_STRING)

    assert gpt3_mock.mock_calls[0] == call(
        classifier.create_prompt(TEXT_STRING),
        time_to_live=60 * 2,
        max_retries=4,
        retry_interval=[
            5,
            15,
            30,
            60,
        ],
        upload_id=None,
        analysis_id=analysis.id,
    )


def test_classifier_does_not_include_a_label_twice(mocker):
    gpt_response = '''
Computer Science
Software Engineering and Security
Computer Science
Theoretical Computer Science
'''

    mocker.patch('tools.text.ai.gpt3', return_value=gpt_response)

    classifier = SubjectClassifier.create_classifier_for('lecture')

    result = classifier.classify(TEXT_STRING)

    assert result == ['Computer Science', 'Software Engineering and Security', 'Theoretical Computer Science']
