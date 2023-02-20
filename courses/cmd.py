from db.crud import find_course_by_course_code
from tools.web.crawler import (
    scrape_course_groups,
    scrape_courses_from_group,
)
from db.models import Course


def fetch_kth_courses():
    course_groups = scrape_course_groups()
    print(f'found {len(course_groups)} course groups')

    courses = {}

    for url in course_groups:
        print(f'crawling {url}')

        courses_in_group = scrape_courses_from_group(url)
        print(f'found {len(courses_in_group)} courses')

        for course in courses_in_group:
            code = course[0]
            name = course[1]
            points = course[2]
            cycle = course[3]

            if code not in courses:
                courses[code] = {
                    'english_name': '',
                    'swedish_name': '',
                    'cycle': '',
                    'points': '',
                }

            if '?l=en' in url:
                courses[code]['english_name'] = name
                courses[code]['cycle'] = cycle
                courses[code]['points'] = points

            if '?l=sv' in url:
                courses[code]['swedish_name'] = name

    print(f'total courses found: {len(courses.keys())}')
    print('saving courses to database')
    new = 0
    seen = 0
    for course_code in courses:
        course = find_course_by_course_code(course_code)
        if course is None:
            new += 1
            course = Course(
                course_code=course_code,
                swedish_name=courses[course_code]['swedish_name'],
                english_name=courses[course_code]['english_name'],
                points=courses[course_code]['points'],
                cycle=courses[course_code]['cycle'],
            )
        else:
            seen += 1
            course.course_code = course_code
            course.swedish_name = courses[course_code]['swedish_name']
            course.english_name = courses[course_code]['english_name']
            course.points = courses[course_code]['points']
            course.cycle = courses[course_code]['cycle']

        course.save()

    print(f'done. found {new} new courses, and updated {seen} existing courses.')
