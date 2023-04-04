from db.models import Course


def test_get_course_by_course_code(api_client):
    course = Course(
        course_code='SF1626',
        swedish_name='Flervariabelanalys',
        english_name='Calculus in Several Variables',
        points='6.0 hp',
        cycle='First cycle',
    )
    course.save()

    response = api_client.get('/courses/SF1626')

    assert response.json()['display_name'] == 'Flervariabelanalys'
