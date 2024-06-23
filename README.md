# stickyNotePrinter
Utilities for printing to a Nemonic sticky note/label printer

This is a set of utilities developed for the [Mangoslab Nemonic Gen 2 (MIP-201)](https://www.nemonic.me/nemonicGen2) 
sticky note/label printer.

# Architecture
This is a Python 3 script utilizing [ReportLab](https://www.reportlab.com/) to take a string and format it to fit on 
the page. This is then output to a PDF and sent using `lpr` to the printer.

# Platform support
Tested on macOS. Should work on Linux. Could work in Windows with some command line parameter tweaks.

# Features
* Dry run mode displays the PDF
* TODO: Generate a checklist from a comma separated list
* TODO: Handle images

# Installation
1. Setup virtual environment: `./setup`

# Examples
* Display a 3x2" label: `./printNotes -m label2 "This is a test" -d`
* Print a 3x2" label: `./printNotes -m label2 "This is a test"`
