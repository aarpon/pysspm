# Simple Scientific Project Manager (sspm)

Simple, platform-independent command-line tool to manage scientific projects.


## Installation

`sspm` requires **Python 3.10 or newer** to run. To install, run the following from a console:

```bash
$ pip install pysspm
```

You can check the installation with:

```bash
$ sspm version
```

Alternatively, you can use the following calls to install `sspm` in editable mode for development:

```bash
$ git clone https://github.com/aarpon/pysspm.git
$ cd pysspm
$ pip install -e .
```

## Usage

The end-user documentation can be found in [docs/index.html](docs/index.md).

## API

To build the developer documentation, use the following:

```bash
$ cd pysspm
$ .\build_docs.bat   # Windows
$ ./build_docs.sh    # Linux or macOS
```

The generated documentation will be in `docs/api`.

