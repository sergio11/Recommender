from setuptools import setup

setup(
    name='Recommender',
    version='1.0',
    install_requires=[
        "flask",
        "osbrain",
        "sklearn",
        "numpy",
        "geopy",
        "matplotlib",
        "scipy",
        "pathlib",
        "Pyro4",
        "pandas"
    ],
    packages=[],
    url='https://github.com/slaanevil/Recommender',
    license='BSD',
    author='BISITE',
    author_email='',
    description='MAS OsBrain Recommender System'
)
