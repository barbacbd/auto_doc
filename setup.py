from setuptools import setup, find_packages
from os import path
from json import loads


this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

with open("about.json") as about:
    jd = loads(about.read())
    
setup(
    name=jd['project'],
    version=jd['version'],
    license='MIT',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    python_requires='>=3.0, <4.0',
    install_requires=[
        'Sphinx',
        'sphinx-rtd-theme',
        'jinja2',
        'pyyaml'
    ],
    entry_points={
        'console_scripts': [
            'docu=autodoc_ext.__main__:main'
        ]
    },
    package_data={'': ['*.j2']},
    url=jd['url'],
    download_url='{}/archive/v_{}.tar.gz'.format(jd["url"], jd["version"].replace(".", "")),
    description='Spinx Autodoc extension that will automatically create and cleanup artifacts.',
    author=jd['author'],
    author_email=jd['email'],
    include_package_data=True,
    zip_safe=False
)
