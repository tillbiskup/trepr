import setuptools
import os

with open(os.path.join(os.path.dirname(__file__), 'VERSION')) as version_file:
    version = version_file.read().strip()

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as f:
    readme = f.read()

with open(os.path.join(os.path.dirname(__file__), 'LICENSE')) as f:
    license_ = f.read()

setuptools.setup(
    name='trepr',
    version=version,
    description='TREPR processing and analysis routines.',
    long_description=readme,
    long_description_content_type='text/x-rst',
    author='Jara Popp, Till Biskup',
    author_email='j.popp@gmx.ch',
    url='',
    license=license_,
    packages=setuptool.find_packages(exclude=('doc')),
    keywords=[
        'spectroscopy'
        'trepr'
        'data processing and analysis'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Intended Audience :: Science/Research',
        'Development Status :: 3 - Alpha',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development :: Libraries :: Application Frameworks'
    ],
    install_requires=[
        'aspecd',
        'cycler',
        'kiwisolver',
        'matplotlib',
        'numpy',
        'pyparsing',
        'python-dateutil',
        'six'
    ],
    python_requires='>=3',
)
