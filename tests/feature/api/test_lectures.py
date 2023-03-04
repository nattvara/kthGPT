from db.models import Lecture, Analysis


def test_get_all_lectures(api_client):
    id = 'some_id'

    lecture = Lecture(public_id=id, language='sv')
    lecture.save()

    analysis = Analysis(lecture_id=lecture.id)
    analysis.save()

    response = api_client.get('/lectures')

    assert response.json()[0]['public_id'] == id
