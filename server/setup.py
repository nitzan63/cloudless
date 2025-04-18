from setuptools import setup, find_packages

setup(
    name="cloudless-server",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "flask",
        "flask-cors",
        "google-cloud-storage",
        "ray",
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-cov",
        ]
    }
) 