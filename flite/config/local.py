import os
from .common import Common
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Local(Common):
    DEBUG = True

    # Testing
    INSTALLED_APPS = Common.INSTALLED_APPS
    INSTALLED_APPS += ('django_nose', 'django_extensions')
    TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
    NOSE_ARGS = [
        BASE_DIR,
        '-s',
        '--nologcapture',
        '--with-coverage',
        '--with-progressive',
        '--cover-package=flite'
    ]

    # Mail
    EMAIL_HOST = 'mailpit'
    EMAIL_PORT = 1025
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    COVERAGE_EXCLUDES_FOLDERS = ['flite/users/migrations/*']