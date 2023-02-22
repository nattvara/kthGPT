from typing import List, Optional
import peewee
import re

from db.crud import (
    find_all_courses_relations_for_course_group_id,
    find_all_courses_relations_for_course_id,
)

from .base import Base
from .lecture import Lecture


# for grouping courses such as SF19XY
class CourseGroup(Base):
    course_code = peewee.CharField(null=False, index=True, unique=True)
    swedish_name = peewee.CharField(null=False)
    english_name = peewee.CharField(null=False)


# crawled courses
class Course(Base):
    course_code = peewee.CharField(null=False, index=True, unique=True)
    group_id = peewee.ForeignKeyField(CourseGroup, null=True, backref='coursegroup')
    swedish_name = peewee.CharField(null=False)
    english_name = peewee.CharField(null=False)
    points = peewee.CharField(null=False)
    cycle = peewee.CharField(null=False)


class CourseLectureRelation(Base):
    lecture_id = peewee.ForeignKeyField(Lecture, null=False, backref='lecture', on_delete='cascade')
    course_id = peewee.ForeignKeyField(Course, null=True, backref='course', on_delete='cascade')
    group_id = peewee.ForeignKeyField(CourseGroup, null=True, backref='coursegroup', on_delete='cascade')


# Wrapper around both course group and courses
class CourseWrapper:

    def __init__(
        self,
        course_code: str,
        swedish_name: str,
        english_name: str,
        source: int,
        points: Optional[str] = None,
        cycle: Optional[str] = None,
        alternate_course_codes: List[str] = [],
        alternate_english_names: List[str] = [],
        alternate_swedish_names: List[str] = [],
        course_id: Optional[int] = None,
        course_group_id: Optional[int] = None,
    ) -> None:
        self.course_code = course_code
        self.swedish_name = swedish_name
        self.english_name = english_name
        self.points = points
        self.cycle = cycle
        self.source = source
        self.alternate_course_codes = alternate_course_codes
        self.alternate_english_names = alternate_english_names
        self.alternate_swedish_names = alternate_swedish_names
        self.course_id = course_id
        self.course_group_id = course_group_id

    class Source:
        COURSE = 1
        COURSE_GROUP = 2

    def from_course(course: Course):
        return CourseWrapper(
            course_code=course.course_code,
            swedish_name=course.swedish_name,
            english_name=course.english_name,
            points=course.points,
            cycle=course.cycle,
            source=CourseWrapper.Source.COURSE,
            course_id=course.id,
        )

    def from_course_group(group: CourseGroup):
        alternate_course_codes = []
        alternate_english_names = []
        alternate_swedish_names = []
        courses = Course.filter(Course.group_id == group.id)
        for course in courses:
            alternate_course_codes.append(course.course_code)
            alternate_english_names.append(course.english_name)
            alternate_swedish_names.append(course.swedish_name)

        return CourseWrapper(
            course_code=group.course_code,
            swedish_name=group.swedish_name,
            english_name=group.english_name,
            source=CourseWrapper.Source.COURSE_GROUP,
            alternate_course_codes=alternate_course_codes,
            alternate_english_names=alternate_english_names,
            alternate_swedish_names=alternate_swedish_names,
            course_group_id=group.id,
        )

    def get_display_name(self) -> str:
        regex = re.compile(r'\D*(\d)(\d)*')
        digit = re.search(regex, self.course_code).group(1).strip()
        if int(digit) == 1:
            return self.swedish_name
        return self.english_name

    def get_number_of_lectures(self):
        if self.source == CourseWrapper.Source.COURSE:
            return len(find_all_courses_relations_for_course_id(self.course_id))
        if self.source == CourseWrapper.Source.COURSE_GROUP:
            return len(find_all_courses_relations_for_course_group_id(self.course_group_id))

    def to_doc(self) -> dict:
        return {
            'course_code': self.course_code,
            'display_name': self.get_display_name(),
            'swedish_name': self.swedish_name,
            'english_name': self.english_name,
            'points': self.points,
            'cycle': self.cycle,
            'alternate_course_codes': self.alternate_course_codes,
            'alternate_english_names': self.alternate_english_names,
            'alternate_swedish_names': self.alternate_swedish_names,
            'lectures': self.get_number_of_lectures(),
        }

    def to_small_dict(self) -> dict:
        return {
            'course_code': self.course_code,
            'display_name': self.get_display_name(),
        }
