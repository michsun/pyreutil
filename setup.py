from setuptools import setup

setup(
    name='Markdown-Text Edit',
    version=open('VERSION','r').read().strip(),
    author='michsun',
    description='Scrapes images from popular search engines',
    # packages=find_packages(include=['image_scraper']),
    install_requires=open('requirements.txt').read().splitlines()
)