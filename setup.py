from setuptools import find_packages
from setuptools import setup


setup(
    name='morfologija',
    version='0.1',
    license='BSD',
    packages=find_packages('src'),
    include_package_data=True,
    zip_safe=False,
    package_dir={'': 'src'},
    install_requires=[
        'fn',
        'pyyaml',
        'docopt',
    ],
    entry_points = {
        'console_scripts': [
            'morfologija=morfologija.tools.morfologija:main',
        ],
    },
)
