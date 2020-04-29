from setuptools import setup

setup(
    name='CodeyzDjangoStat',
    version='0.0.1',
    packages=['cdzstat', 'cdzstat.tests', 'cdzstat.migrations'],
    scipts=['static/cds_stat.js'],
    package_data={'cdzstat': ['fixtures/*.json']},
    url='https://github.com/codeyzcom/CodeyzDjangoStat',
    license='MIT',
    author='Yevgeniy Zheleznov',
    author_email='atom@codeyz.com',
    description='Collection and analysis of site traffic'
)
