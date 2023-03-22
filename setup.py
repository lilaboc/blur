from distutils.core import setup


def read_file(fname):
    with open(fname, encoding='utf-8') as f:
        return f.read()


REQUIREMENTS = read_file('requirements.txt').splitlines()[1:]

setup(
    name='blur',
    version='0.0.1',
    packages=['blur'],
    url='',
    license='',
    author='stern',
    author_email='',
    description='',
    install_requires=REQUIREMENTS,
    entry_points={
        'console_scripts': [
            'blur= blur:main',
        ],
    }
)
