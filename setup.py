import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="primehub_job",
    version="0.1.3",
    description="Submit PrimeHub jobs easier",
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=setuptools.find_packages(),
    license='Apache License 2.0',
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3',
    install_requires=['cloudpickle', 'requests', 'ipywidgets'],

)