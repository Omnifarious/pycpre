import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="PyCPre",
    version="0.1",
    author="Eric Hopper",
    author_email="hopper@omnifarious.org",
    description="Copy parts of Twitter's relationship graph to a database.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages("src"),
    package_dir={"": "src"},
    py_modules=[],
    python_requires=">=3.9",
    tests_require=[
        "pytest>=6.2.4",
    ],
    install_requires=[
    ],
    entry_points={
    #    'console_scripts': [
    #        "noneyet = pycpre.main:entrypoint",
    #    ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Environment :: Console",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
    ],
)
