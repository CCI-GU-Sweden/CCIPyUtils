A collection of python utilities used at the Centre for Cellular Imaging at the University of gothenburg.

## Installation
Since these packages are not in any wheel or distribution you need to pip install them from git:

pip install "git+ssh://git@github.com/CCI-GU-Sweden/CCIPyUtils.git@main#egg=ccipy_utils&subdirectory=ccipy-utils"

you can change 'main' to any branch/revision/tag etc you want

Each package needs to be installed separately. Use #egg=ccipy-PACKAGE&subdirectory=ccipy-SUBDIR

### ccipy-omero
Classes and functions for managing OMERO connection and objects

### ccipy-utils
Various  classes, wrappers and functions for simplifying work with python and the rest of the packages here

### ccipy-atlas
Functions for handling Atlas project files and models

### ccipy-yolo-utils
Wrappers and utilities for training and using yolo AI models

### ccipy-stardist-utils
Yeah, you guessed it ;)

### ccipy-extras


* Free software: MIT License

## Features

* TODO

## Credits

This package was created with [Cookiecutter](https://github.com/audreyfeldroy/cookiecutter) and the [audreyfeldroy/cookiecutter-pypackage](https://github.com/audreyfeldroy/cookiecutter-pypackage) project template.
