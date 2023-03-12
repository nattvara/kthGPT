import db.crud as crud
import db.models as models


def test_get_all_courses_includes_courses():
    course1 = models.Course(
        course_code='SF1626',
        swedish_name='Flervarre',
        english_name='Multivariable Calculus',
        points='7.5 hp',
        cycle='First cycle',
    )
    course1.save()
    course2 = models.Course(
        course_code='SF2972',
        swedish_name='Spelteori',
        english_name='Game Theory',
        points='7.5 hp',
        cycle='First cycle',
    )
    course2.save()

    courses = crud.get_all_courses()

    assert len(courses) == 2

    for c in [course1, course2]:
        found = False
        for course in courses:
            if course.course_code == c.course_code:
                found = True

        assert found


def test_get_all_courses_includes_course_groups():
    group1 = models.CourseGroup(
        course_code='SF19XY',
        swedish_name='Sannolikhetsteori och statistik',
        english_name='Probability Theory and Statistics',
        points='7.5 hp',
        cycle='First cycle',
    )
    group1.save()

    course1 = models.Course(
        course_code='SF1912',
        group_id=group1.id,
        swedish_name='Sannolikhetsteori och statistik',
        english_name='Probability Theory and Statistics',
        points='7.5 hp',
        cycle='First cycle',
    )
    course1.save()
    course2 = models.Course(
        course_code='SF1924',
        group_id=group1.id,
        swedish_name='Sannolikhetsteori och statistik',
        english_name='Probability Theory and Statistics',
        points='7.5 hp',
        cycle='First cycle',
    )
    course2.save()
    course3 = models.Course(
        course_code='DD2350',
        swedish_name='Algoritmer, datastrukturer och komplexitet',
        english_name='Algorithms, Data Structures and Complexity',
        points='9.5 hp',
        cycle='First cycle',
    )
    course3.save()

    courses = crud.get_all_courses()

    assert len(courses) == 2

    for c in [course1, course2]:
        found = False
        for course in courses:
            if course.course_code == c.course_code:
                found = True

        # response should only include the group not it's courses
        assert not found

    for c in [group1, course3]:
        found = False
        for course in courses:
            if course.course_code == c.course_code:
                found = True

        # response should contain both group and course without group
        assert found
