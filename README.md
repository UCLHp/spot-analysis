# Spot_Analysis

This repository is used to group all cods relating to the acquisition and
analysis of spot patterns and spot profiles using the a LOGOS scintillator
detector

Currently a non-working version

# logos_module.py

A script containing various functions that are used in both the spot qa and
commissioning scripts

# spot_commissioning.py

A script that converts a folder of raw acquired images in tiff file format into
an excel spreadsheet containing fitted plots to enter into a treatment planning
system software

# spot_qa

A script for ongoing qa that will analyse a predefined grid of spots and write
the results to an access database

# Components

README.md
.gitignore
LICENSE
logos_module.py
spot_commissioning.py
spot_qa.py

# Installation

Do not install, please use latest version of the executable when available

# Requirements

***to be updated on first release!***

tifffile
numpy
easygui

# Risk Assessment

|Risk|Solution|
|If the incorrect files/energies are used for commissioning this may result
in discrepancies between planned and delivered dose - this would be picked up
during testing but will add significant time to trouble shooting|Commissioning
results will always be checked visually during the full process to pick up
errors of this kind|
|If QA test pass incorrectly - this may lead to beam errors not being picked
up|All QA tests should be independently checked|
|If QA tests fail incorrectly - this may add time troubleshooting in set.|All
QA tests should be independently checked|


# Tests

No tests currently included

# Usage

Acquire images and save into a directory along with the active script which
provides the pixel resolution
run the code and navigate to this directory.
***Choose a location to save the results***

# Limitations / Known Bugs

Currently only works for tifffiles

# Contribute

Pull requests are welcome.  
For major changes, please open a ticket first to discuss desired changes:  
[Spot_Analysis/issues](http://github.com/UCLHp/Spot_Analysis/issues)

If making changes, please check all tests and add if required.

# Licence

All code within this package distributed under [GNU GPL-3.0 (or higher)](https://opensource.org/licenses/GPL-3.0).

Full license text contained within the file LICENCE.

# (C) License for all programmes

```
###  Copyright (C) 2020:  Callum Stuart Main Gillies

  #  This program is free software: you can redistribute it and/or modify
  #  it under the terms of the GNU General Public License as published by
  #  the Free Software Foundation, either version 3 of the License, or
  #  (at your option) any later version.

  #  This program is distributed in the hope that it will be useful,
  #  but WITHOUT ANY WARRANTY; without even the implied warranty of
  #  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  #  GNU General Public License for more details.

  #  You should have received a copy of the GNU General Public License
  #  along with this program.  If not, see <http://www.gnu.org/licenses/>.
```
