from setuptools import setup, find_packages

setup(
    name="PyOpticL",
    version="0.0.1",
    packages=find_packages(),
    install_requires=[
        "numpy",
        # FreeCAD should be installed separately as it's not on PyPI
    ],
    include_package_data=True,
    package_data={
        'PyOpticL': [
            'stl/*',
            'font/*'
        ],
    },
    author="UMass Ion Trappers",
    description="Code-to-CAD optical system engineering",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/UMassIonTrappers/PyOpticL",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    python_requires=">=3.6",
)