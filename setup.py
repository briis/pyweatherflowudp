from distutils.core import setup

setup(
    name="pyweatherflowudp",
    packages=["pyweatherflowudp"],
    version="0.0.2",
    license="MIT",
    description="Asynchronous Python library to receive UDP Packets from Weatherflow Weatherstations",
    author="Bjarne Riis",
    author_email="bjarne@briis.com",
    url="https://github.com/briis/pyweatherflowudp",
    keywords=["Weatherflow", "Weather", "UDP", "Home Assistant", "Python"],
    install_requires=[
        "asyncio",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",  # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
