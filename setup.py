from distutils.core import setup
import setuptools
import os

with open(os.path.join(os.path.dirname(__file__), 'VERSION')) as version_file:
    version = version_file.read().strip()

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as f:
    readme = f.read()

setup(
    name='trepr',
    version=version,
    description='TREPR processing and analysis routines.',
    long_description=readme,
    long_description_content_type='text/x-rst',
    author='Jara Popp, Till Biskup, Mirjam Schröder',
    author_email='till@till-biskup.de',
    url='https://www.trepr.de/',
    project_urls={
        "Documentation": "https://docs.trepr.de/",
        "Source": "https://github.com/tillbiskup/trepr",
    },
    packages=setuptools.find_packages(exclude=('doc')),
    keywords=[
        'spectroscopy', 
        'trepr', 
        'data processing and analysis'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Intended Audience :: Science/Research',
        'Development Status :: 4 - Beta',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development :: Libraries :: Application Frameworks'
    ],
    install_requires=[
        'aspecd',
        'jinja2',
        'matplotlib',
        'numpy',
        'scipy',
        'xmltodict',
    ],
    python_requires='>=3.5',
)
