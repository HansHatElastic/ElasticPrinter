from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="elasticprinter",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Virtual macOS printer that posts PDFs to Elasticsearch",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/elasticprinter",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Printing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: MacOS :: MacOS X",
    ],
    python_requires=">=3.8",
    install_requires=[
        "elasticsearch>=8.0.0",
        "PyPDF2>=3.0.0",
        "pyyaml>=6.0",
        "requests>=2.28.0",
        "python-dateutil>=2.8.0",
    ],
    entry_points={
        "console_scripts": [
            "elasticprinter=main:main",
        ],
    },
)
