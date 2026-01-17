import os
from setuptools import setup, find_packages

current_dir = os.path.dirname(os.path.abspath(__file__))


def read(filename):
    fullpath = os.path.join(current_dir, filename)
    try:
        with open(fullpath) as f:
            return f.read()
    except Exception:
        return ""


setup(
    name='django-ftpserver',
    version='0.9.0',
    description="FTP server application for Django.",
    long_description=read('README.rst'),
    packages=find_packages(),
    author='Shinya Okano',
    author_email='tokibito@gmail.com',
    url='https://github.com/tokibito/django-ftpserver',
    install_requires=['Django>=3.2', 'pyftpdlib'],
    extras_require={
        'develop': [
            'pytest', 'flake8', 'pytest-django',
            'tox', 'wheel',
        ],
    },
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ])
