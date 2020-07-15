import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sherloq",
    version="1",
    description="An open source image forensic toolset",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/GuidoBartoli/sherloq",
    packages=setuptools.find_packages(),
    include_package_data=True,
    requires_python=">=3.6",
    install_requires = [
        "astor",
        "concurrent-iterator",
        "keras-applications",
        "lxml",
        "opencv-contrib-python-headless",
        "pandas",
        "pyside2",
        "python-magic",
        "scikit-image",
        "scikit-learn",
        "sewar",
        "tensorflow",
        "xgboost"
    ],
    classifiers= [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GPLv3 License",
        "Operating System :: OS Independent",
    ],
    entry_points = {
        "console_scripts" : [
            "sherloq = gui.sherloq:main"
        ]
    }
)
