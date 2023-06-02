from setuptools import setup, find_packages


setup(
    name='pid',
    version='0.1.2',
    packages=find_packages(),
    tests_require=[
        'pytest==7.3.1',
    ],
    python_requires='>=3.11'
)
