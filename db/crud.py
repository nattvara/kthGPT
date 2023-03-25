from typing import Union


# URL
def get_url_by_sha(sha: str):
    from db.models.url import URL
    return URL.filter(URL.url_hash == sha).first()


# Lecture
def get_lecture_by_public_id_and_language(id: str, language: str):
    from db.models.lecture import Lecture
    return Lecture.filter(Lecture.public_id == id).filter(Lecture.language == language).first()


def get_all_lectures():
    from db.models.lecture import Lecture
    query = Lecture.select().order_by(Lecture.created_at.asc())

    lectures = []
    for lecture in query:
        lectures.append(lecture)

    return lectures


def get_all_ready_lectures():
    from db.models.lecture import Analysis
    lectures = get_all_lectures()

    out = []
    for lecture in lectures:
        if lecture.get_last_analysis().state == Analysis.State.READY:
            out.append(lecture)

    return out


def get_all_denied_lectures():
    from db.models.lecture import Analysis
    lectures = get_all_lectures()

    out = []
    for lecture in lectures:
        if lecture.get_last_analysis().state == Analysis.State.DENIED:
            out.append(lecture)

    return out


def get_all_failed_lectures():
    from db.models.lecture import Analysis
    lectures = get_all_lectures()

    out = []
    for lecture in lectures:
        if lecture.get_last_analysis().state == Analysis.State.FAILURE:
            out.append(lecture)

    return out


def get_unfinished_lectures():
    from db.models.lecture import Analysis
    lectures = get_all_lectures()

    out = []
    for lecture in lectures:
        if lecture.get_last_analysis().state not in [
            Analysis.State.READY,
            Analysis.State.DENIED,
        ]:
            out.append(lecture)

    return out


# Analysis
def get_all_analysis_for_lecture(lecture_id: int):
    from db.models import Analysis
    query = Analysis.filter(Analysis.lecture_id == lecture_id)

    out = []
    for a in query:
        out.append(a)

    return out


def delete_all_except_last_message_in_analysis(analysis_id: int):
    from db.models import Analysis, Message
    a = Analysis.get(analysis_id)
    last_message = a.get_last_message()

    Message.delete().where(
        Message.id != last_message
    ).where(
        Message.analysis_id == analysis_id
    ).execute()


# Query
def get_most_recent_query_by_sha(lecture, sha: str):
    from db.models.query import Query
    return Query.filter(
        Query.lecture_id == lecture.id
    ).filter(
        Query.query_hash == sha
    ).filter(
        Query.cache_is_valid == True  # noqa: E712
    ).order_by(
        Query.modified_at.desc()
    ).first()


def create_query(lecture, query_string: str):
    from db.models.query import Query
    query = Query(lecture_id=lecture.id, query_string=query_string)
    query.save()
    return query


def find_all_queries_for_lecture(lecture):
    from db.models.query import Query
    return Query.select().where(Query.lecture_id == lecture.id)


# Message
def save_message_for_analysis(analysis, title: str, body: Union[str, None] = None):
    from db.models.message import Message
    msg = Message(analysis_id=analysis.id, title=title, body=body)
    msg.save()


# Course
def find_course_by_course_code(code: str):
    from db.models.course import Course
    return Course.filter(Course.course_code == code).first()


def get_all_courses():
    from db.models.course import Course, CourseGroup, CourseWrapper
    out = []

    courses = Course.filter(Course.group_id == None)  # noqa: E711
    for course in courses:
        out.append(CourseWrapper.from_course(course))

    courses_groups = CourseGroup.select()
    for group in courses_groups:
        out.append(CourseWrapper.from_course_group(group))

    return out


def find_course_code(course_code: str):
    from db.models.course import Course, CourseGroup, CourseWrapper

    course = CourseGroup.filter(CourseGroup.course_code == course_code).first()
    if course is not None:
        return CourseWrapper.from_course_group(course)

    course = Course.filter(Course.course_code == course_code).first()
    if course is not None:
        return CourseWrapper.from_course(course)

    return None


def find_all_courses_relations_for_course_group_id(id: int):
    from db.models.course import CourseLectureRelation
    relations = CourseLectureRelation.filter(CourseLectureRelation.group_id == id)
    return relations


def find_all_courses_relations_for_course_id(id: int):
    from db.models.course import CourseLectureRelation
    relations = CourseLectureRelation.filter(CourseLectureRelation.course_id == id)
    return relations


def find_all_courses_relations_for_lecture_id(id: int):
    from db.models.course import CourseLectureRelation
    relations = CourseLectureRelation.filter(CourseLectureRelation.lecture_id == id)
    return relations


def find_all_courses_for_lecture_id(id: int):
    from db.models.course import Course, CourseGroup, CourseWrapper, CourseLectureRelation
    out = []
    relations = CourseLectureRelation.filter(CourseLectureRelation.lecture_id == id)
    for relation in relations:
        if relation.course_id is not None:
            out.append(CourseWrapper.from_course(
                Course.get(id=relation.course_id))
            )
        elif relation.group_id is not None:
            out.append(CourseWrapper.from_course_group(
                CourseGroup.get(id=relation.group_id))
            )

    return out


def create_relation_between_lecture_and_course(lecture_id: int, course_id: int):
    from db.models.course import CourseLectureRelation
    relation = CourseLectureRelation(
        lecture_id=lecture_id,
        course_id=course_id,
    )
    relation.save()


def create_relation_between_lecture_and_course_group(lecture_id: int, group_id: int):
    from db.models.course import CourseLectureRelation
    relation = CourseLectureRelation(
        lecture_id=lecture_id,
        group_id=group_id
    )
    relation.save()


def find_relation_between_lecture_and_course(lecture_id: int, course_id: int):
    from db.models.course import CourseLectureRelation
    return CourseLectureRelation.filter(CourseLectureRelation.lecture_id == lecture_id).filter(CourseLectureRelation.course_id == course_id).first()  # noqa: E501


def find_relation_between_lecture_and_course_group(lecture_id: int, group_id: int):
    from db.models.course import CourseLectureRelation
    return CourseLectureRelation.filter(CourseLectureRelation.lecture_id == lecture_id).filter(CourseLectureRelation.group_id == group_id).first()  # noqa: E501


def delete_lecture_course_relation(id: int):
    from db.models.course import CourseLectureRelation
    return CourseLectureRelation.delete().where(CourseLectureRelation.id == id).execute()


# ImageUpload
def get_image_upload_by_public_id(id: str):
    from db.models import ImageUpload
    return ImageUpload.filter(ImageUpload.public_id == id).first()


def get_image_upload_by_image_sha(sha: str):
    from db.models import ImageUpload
    return ImageUpload.filter(ImageUpload.image_sha == sha).first()


# Mathpix requests
def get_mathpix_requests_by_image_upload_id(id: int):
    from db.models import MathpixRequest
    return MathpixRequest.filter(MathpixRequest.image_upload_id == id)
