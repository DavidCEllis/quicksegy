from setuptools import setup, find_packages

__version__ = '0.0.1'
__author__ = 'DavidCEllis'


setup(
    name='quicksegy',
    version=__version__,

    packages=find_packages(),
    url='',
    license='MIT',
    description='Quick tool for handling SEG-Y metadata and geometry.',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 1 - Early Development',
        'Intended Audience :: Geoscientists',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
    ],
    extras_require={
        'geometry': ['shapely', 'fiona']
    },
    tests_require=[
        'pytest',
        'hypothesis',
    ]
)
