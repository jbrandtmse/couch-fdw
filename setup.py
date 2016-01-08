from setuptools import setup, find_packages, Extension

setup(
        name='couchfdw',
        version='0.0.1',
        author='Marcelo Daparte',
        license='Postgresql',
        packages=['couchfdw'],
        install_requires=[
            'couchquery',
            'simplejson',
            'multicorn'
        ]
)
