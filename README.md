PyCSGScriptLive
==============
PyCSGScriptLive is an environment composed of a python DSL for CSG description and an interactive editor.
The purpose of such an environment is to ease the CSG description that is often used to describe solid objects for physical simulations, such as electromagnetic fields simulations.

#pyCSGScript
A simple python DSL for CSG description.
It is a set of python classes to describe solid geometries, and methods to manipulate them. Geometries can be tagged with a material id meant to be used in physical simulations.
The provided implementation is used to obtain a mesh representation for rendering but this implementation is meant to be changed (by extension or altogether) according to the final data representation that is desired.
For instance another implementation could be provided to obtain a volume representation aimed at physical simulations.

#pyCSGScriptLive
An editor with OpenGL preview for pyCSGScript.
The preview changes dynamically with the code in the editor.

##INSTALLATION for Ubuntu 12.04 - 13.10

ensure the following packages are installed:

* python-qt4
* python-pyside (only needed for pyPolyCSG examples)
* python-numpy
* python-boost
* autoconf

download carve 1.4 at http://code.google.com/p/carve/downloads/detail?name=carve-1.4.0.tgz&can=2&q=

extract into a "carve" folder

execute:

```bash
$ ./autogen.sh
$ ./configure
```

go to the "lib" subfolder then type

```bash
$ make
$ sudo make install
$ sudo ldconfig
```

go to the pyPolyCSG (patched version) folder and type

```bash
$ sudo python setup.py install
```

go to the pyCSGScript folder and type
```bash
$ sudo python setup.py install
```

if all goes right you can now launch pyCSGSCriptLive.py. enjoy! :)
