from setuptools import setup, find_packages

setup(
    name='wilitools',
    version='0.0.0',
    description='db & suggester of WiLI',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    author='ShinagawaKazemaru',
    author_email='marukazemaru0@gmail.com',
    license='MIT',

    install_requires=['numpy'],
    python_requires='>=3',
    packages=find_packages(where='src'),
    package_dir={'': 'src'}
)
