import setuptools
from ws_tool_name._version import __version__

tool_name = 'ws_top10_rejected_libs'

setuptools.setup(
    name=f"ws_{tool_name}",
    entry_points={
        'console_scripts': [
            f'{tool_name}=ws_{tool_name}.{tool_name}:main'
        ]},
    version=__version__,
    author="Tidhar Meltzer",
    author_email="tidhar.meltzer@whitesourcesoftware.com",
    description="Get a list of the top-10 rejected libraries in your WhiteSource inventory",
    url='https://github.com/whitesource-ps/ws-tool-name',
    license='LICENSE.txt',
    packages=setuptools.find_packages(),
    python_requires='>=3.6',
    install_requires=[line.strip() for line in open("requirements.txt").readlines()],
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)
