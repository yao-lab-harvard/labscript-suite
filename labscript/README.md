<img src="https://raw.githubusercontent.com/labscript-suite/labscript-suite/master/art/labscript_32nx32n.svg" height="64" alt="the labscript suite" align="right">

# the _labscript suite_ » labscript

### Expressive composition of hardware-timed experiments

[![Actions Status](https://github.com/labscript-suite/labscript/workflows/Build%20and%20Release/badge.svg)](https://github.com/labscript-suite/labscript/actions)
[![License](https://img.shields.io/pypi/l/labscript.svg)](https://github.com/labscript-suite/labscript/raw/master/LICENSE.txt)
[![Python Version](https://img.shields.io/pypi/pyversions/labscript.svg)](https://python.org)
[![PyPI](https://img.shields.io/pypi/v/labscript.svg)](https://pypi.org/project/labscript)
[![Conda Version](https://img.shields.io/conda/v/labscript-suite/labscript)](https://anaconda.org/labscript-suite/labscript)
[![Google Group](https://img.shields.io/badge/Google%20Group-labscriptsuite-blue.svg)](https://groups.google.com/forum/#!forum/labscriptsuite)
<!-- [![DOI](http://img.shields.io/badge/DOI-10.1063%2F1.4817213-0F79D0.svg)](https://doi.org/10.1063/1.4817213) -->


The **labscript** Python library permits expressive composition of hardware-timed experiments. Hardware connections and experiment logic are described using Python classes, functions and methods, which labscript translates into low-level primitives specific to individual instruments.

<!-- Thus the experimenter writes a labscript primitive such as `laser_beam.constant(t=3, value=100, units='mW')` and this
will add an entry to the table of instructions for whichever digital-to-analogue converter is controlling the a laser beam to output 100 mW, 3 seconds after the experiment commences. This is a simple example, but has advantages over having a human write tables of instructions for scientific instruments directly. -->


## Installation

labscript is distributed as a Python package on [PyPI](https://pypi.org/user/labscript-suite) and [Anaconda Cloud](https://anaconda.org/labscript-suite), and should be installed with other components of the _labscript suite_. Please see the [installation guide](https://docs.labscriptsuite.org/en/latest/installation) for details.
