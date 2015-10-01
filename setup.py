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
    version='0.3.2',
    description="FTP server application for Django.",
    long_description=read('README.rst'),
    package_dir={'': 'src'},
    packages=find_packages('src'),
    author='Shinya Okano',
    author_email='tokibito@gmail.com',
    url='https://github.com/tokibito/django-ftpserver',
    install_requires=['Django>=1.4', 'pyftpdlib'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'License :: OSI Approved :: MIT License',
    ])
