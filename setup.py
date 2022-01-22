from setuptools import setup

setup(
    name='Markdown-Text Edit',
    version=open('VERSION','r').read().strip(),
    author='michsun',
    author_email='',
    description='',
    # packages=find_packages(include=['']),
    install_requires=open('requirements.txt').read().splitlines(),
    entry_points= {
        'console_scripts': ['mdtedit = mdtedit.__main__:main']
    }
)