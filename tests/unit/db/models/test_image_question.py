
from db.crud import get_image_question_by_public_id
from db.models import ImageQuestion, ImageQuestionHit


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

    assert hit.response is None
    assert hit.cache_is_valid is True

    # Test accessor from ImageQuestion
    assert len(image_question.hits()) == 1
    assert image_question.hits()[0].id == hit.id
