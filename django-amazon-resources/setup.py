import os
from setuptools import setup, find_packages

from amazon_resources import VERSION

f = open(os.path.join(os.path.dirname(__file__), 'README.rst'))
readme = f.read()
f.close()

setup(
    name='django-amazon-resources',
    version=".".join(map(str, VERSION)),
    description='display amazon resources on your site',
    long_description=readme,
    author='Charles Leifer',
    author_email='coleifer@gmail.com',
    url='http://github.com/coleifer/django-amazon-resources/tree/master',
    packages=find_packages(),
    package_data = {
        'amazon_resources': [
            'templates/*.html',
            'templates/*/*.html',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
)
