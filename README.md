PyCSGScriptLive
==============
PyCSGScriptLive is an environment composed of a language (based on python) and an editor, for CSG description.

#pyCSGScript
Simple python library for CSG description.

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
