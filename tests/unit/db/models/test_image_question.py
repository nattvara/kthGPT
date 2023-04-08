
from db.crud import get_image_question_by_public_id
from db.models import ImageQuestion, ImageQuestionHit
import tools.text.prompts as prompts
import tools.text.ai


def test_image_question_can_be_saved(image_upload):
    public_id = ImageQuestion.make_public_id()

    question = ImageQuestion(
        public_id=public_id,
        image_upload_id=image_upload.id,
        query_string='help me',
    )
    question.save()

    saved = get_image_question_by_public_id(public_id)
    assert question.id == saved.id


def test_image_question_hit_can_be_saved(image_question, analysed_lecture):
    hit = ImageQuestionHit(
        public_id=ImageQuestionHit.make_public_id(),
        image_question_id=image_question.id,
        lecture_id=analysed_lecture.id,
    )
    hit.save()

    assert hit.answer is None
    assert hit.relevance is None
    assert hit.cache_is_valid is True

    # Test accessor from ImageQuestion
    assert len(image_question.hits()) == 1
    assert image_question.hits()[0].id == hit.id


def test_image_question_hit_can_compute_answer(mocker, image_question, analysed_lecture):
    answer = 'some ai wizardry'
    mocker.patch('tools.text.ai.gpt3', return_value=answer)

    hit = ImageQuestionHit(
        public_id=ImageQuestionHit.make_public_id(),
        image_question_id=image_question.id,
        lecture_id=analysed_lecture.id,
    )
    hit.save()

    hit.create_answer(tools.text.ai, prompts)
    hit.save()

    assert hit.answer == answer


def test_image_question_hit_answer_is_cached(mocker, image_question, analysed_lecture):
    answer = 'some ai wizardry'
    gpt3_mock = mocker.patch('tools.text.ai.gpt3', return_value=answer)

    hit = ImageQuestionHit(
        public_id=ImageQuestionHit.make_public_id(),
        image_question_id=image_question.id,
        lecture_id=analysed_lecture.id,
    )
    hit.save()

    def func():
        hit.create_answer(tools.text.ai, prompts)
        hit.save()

    # call the function a few times
    func()
    func()
    func()

    assert hit.answer == answer
    assert gpt3_mock.call_count == 1


def test_image_question_hit_answer_can_be_expired(mocker, image_question, analysed_lecture):
    answer = 'some ai wizardry'
    gpt3_mock = mocker.patch('tools.text.ai.gpt3', return_value=answer)

    hit = ImageQuestionHit(
        public_id=ImageQuestionHit.make_public_id(),
        image_question_id=image_question.id,
        lecture_id=analysed_lecture.id,
    )
    hit.save()

    def func():
        hit.create_answer(tools.text.ai, prompts)
        hit.save()

    func()
    func()
    func()

    assert hit.answer == answer
    assert gpt3_mock.call_count == 1

    hit.cache_is_valid = False
    hit.save()
    func()
    func()

    assert hit.answer == answer
    assert gpt3_mock.call_count == 2


def test_image_question_hit_can_compute_relevance(mocker, image_question, analysed_lecture):
    relevance = 'the ai did wizardry'
    mocker.patch('tools.text.ai.gpt3', return_value=relevance)

    hit = ImageQuestionHit(
        public_id=ImageQuestionHit.make_public_id(),
        image_question_id=image_question.id,
        lecture_id=analysed_lecture.id,
    )
    hit.save()

    hit.create_relevance(tools.text.ai, prompts)
    hit.save()

    assert hit.relevance == relevance


def test_image_question_hit_relevance_is_cached(mocker, image_question, analysed_lecture):
    relevance = 'the ai did wizardry'
    gpt3_mock = mocker.patch('tools.text.ai.gpt3', return_value=relevance)

    hit = ImageQuestionHit(
        public_id=ImageQuestionHit.make_public_id(),
        image_question_id=image_question.id,
        lecture_id=analysed_lecture.id,
    )
    hit.save()

    def func():
        hit.create_relevance(tools.text.ai, prompts)
        hit.save()

    # call the function a few times
    func()
    func()
    func()

    assert hit.relevance == relevance
    assert gpt3_mock.call_count == 1


def test_image_question_hit_relevance_can_be_expired(mocker, image_question, analysed_lecture):
    relevance = 'the ai did wizardry'
    gpt3_mock = mocker.patch('tools.text.ai.gpt3', return_value=relevance)

    hit = ImageQuestionHit(
        public_id=ImageQuestionHit.make_public_id(),
        image_question_id=image_question.id,
        lecture_id=analysed_lecture.id,
    )
    hit.save()

    def func():
        hit.create_relevance(tools.text.ai, prompts)
        hit.save()

    func()
    func()
    func()

    assert hit.relevance == relevance
    assert gpt3_mock.call_count == 1

    hit.cache_is_valid = False
    hit.save()
    func()
    func()

    assert hit.relevance == relevance
    assert gpt3_mock.call_count == 2
