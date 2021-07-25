import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="scancode_glc_plugin",
    version="0.0.1",
    author="AvishrantSh (Avishrant Sharma)",
    author_email="<avishrants@gmail.com>",
    description="Django middleware to enforce login before accessing certain URL's",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AvishrantsSh/AuthRequiredMiddleware",
    project_urls={
        "Bug Tracker": "https://github.com/AvishrantsSh/AuthRequiredMiddleware/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    package_dir={"": "src"},
    include_package_data=True,
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)
