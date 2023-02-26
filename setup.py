"""Setup kthgpt."""

from setuptools import setup, find_packages

setup(
    name='kthgpt',
    version='1.0',
    description='Ask GPT-3 questions about KTH lectures',
    author='Ludwig Kristoffersson',
    author_email='ludwig@kristoffersson.org',
    python_requires='>=3.10',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'pytest==7.2.1',
        'playwright==1.30.0',
        'pytest-playwright==0.3.0',
        'fastapi==0.91.0',
        'uvicorn==0.20.0',
        'pydantic[dotenv]==1.10.4',
        'peewee==3.15.4',
        'psycopg2== 2.9.5',
        'rq==1.12.0',
        'ffmpeg-python==0.2.0',
        'openai-whisper==20230124',
        'openai==0.26.5',
        'tiktoken==0.2.0',
        'validators==0.20.0',
        'pytz==2022.7.1'
    ],
    entry_points={
        'console_scripts': [
            'create_db_schema = db.schema:create',
            'create_migration = db.migrations:create_migration',
            'migrate_up = db.migrations:run_migrations',
            'migrate_down = db.migrations:rollback',
            'analysis_queues_restart = jobs:analysis_queues_restart',
            'dispatch_fetch_metadata_for_all_lectures = jobs.cmd:fetch_metadata_for_all_lectures',
            'dispatch_capture_preview_for_all_lectures = jobs.cmd:capture_preview_for_all_lectures',
            'dispatch_cleanup_for_all_lectures = jobs.cmd:cleanup_for_all_lectures',
            'fetch_kth_courses = courses.cmd:fetch_kth_courses',
            'index_all_courses = index.cmd:index_all_courses',
            'index_all_lectures = index.cmd:index_all_lectures',
        ]
    },
    tests_require=[],
)
