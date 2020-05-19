from setuptools import setup

setup(
    name='github-backup',
    version='1.0',
    description='Github Backup',
    author='Philippe Remy',
    license='MIT',
    long_description_content_type='text/markdown',
    long_description=open('README.md').read(),
    packages=['gitbackup'],
    entry_points={
        'console_scripts': [
            'gitbackup=gitbackup.cli:cli'
        ]},
    install_requires=[
        'gitpython',
        'PyGithub',
        'tqdm',
        'click'
    ]
)
