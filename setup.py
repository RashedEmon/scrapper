# Automatically created by: scrapyd-deploy
import os
from setuptools import setup, find_packages


def read_requirements():
    """Read the requirements.txt file and return a list of requirements."""
    requirements = []
    if os.path.exists('scrapper/requirements.txt'):
        with open('scrapper/requirements.txt', 'r') as req_file:
            for line in req_file:
                # Strip whitespace and ignore empty lines or comments
                line = line.strip()
                if line and not line.startswith('#'):
                    requirements.append(line)
    return requirements

print(read_requirements())

setup(
    name             = 'travelai_scrapper',
    version          = '1.0',
    packages         = find_packages(),
    install_requires = read_requirements(),
    entry_points     = {'scrapy': ['settings = scrapper.settings']},
    package_data={
        'scrapper': ['*.json', '*.txt'],
    },
    include_package_data=True,
)
