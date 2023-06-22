Installing BEATS TomoScan
==========================

This page includes information about the needed packages to run the DAQ system.

Prerequisites
--------------

The following should be installed on the computer before running the system:

* Linux redhat based OS (This work has been done under CentOS 7.4, however, there should be no reason to not work on other distributions)
* EPICS BEATS IOCs (motion and scan IOCs)
* Python 3.9
* QT 4.1.0 based on 5.9.7.


Python virtual environment
---------------------------
venv module of Python is being used as a virtual environment for this setup.

The venv module of python provides support for creating **virtual environments** that is isolated from system site directories. Normally, each virtual environment has its own Python binary (which matches the version of the binary that was used to create this environment) and can have its own independent set of installed Python packages in its site directories.

to install and create venv:
::

	$ pip3.9 install virtualenv
	$ python3.9 -m venv ${Home}/DAQ/SW/venv3.9

to create alias of you environment:
::

	$ vi ~/.bashrc

add the following line to the file:
::

	alias p3='source ${Home}/DAQ/SW/venv3.9/bin/activate'

resource your bashrc:
::

	source ~/.bashrc


Packages and libraries
-----------------------

The tool needs set of python packages and Qt libraries installed and configured.

Pyhon packages:
...............

The list below contains the list of python packages needed for the scanning tool to run. After activating the python virtual environment (by typing **p3** in the terminal), you can use **pip** to install them in the virtual environment or you can copy this list in a text file (requirements.txt) and install them at once using this command (pip install -r requirements.txt)

::

	pymsgbox
	pyepics
	h5py
	pvapy
	paramiko
	colorama
	PyQt5


.. _qt:

Qt and its libraries
.....................


	1. Install epics from SESAME's local repo.
	2. Download Qt creator: https://drive.sesame.org.jo/owncloud/index.php/s/LO3GLyDkPMWZKU9.
	3. Install qt-creator-opensource-linux-x86_64-4.13.3.run.
	4. Install epics-qt, qt5, qwt, or anything related to *qt* packages by ``yum`` command.
	5. Go to ``.bashrc`` and copy the following:

	::

		export EPICS_BASE='/opt/epics/base'
		export EPICS_HOST_ARCH=linux-x86_64
		export PATH=${PATH}:/opt/qtcreator-4.13.3/bin/
		export QWT_ROOT=/usr/local/qwt-6.1.3
		export QWT_INCLUDE_PATH=${QWT_ROOT}/include
		export QE_TARGET_DIR=/usr/local/epics-qt
		export PATH=${EPICS_BASE}/bin/$EPICS_HOST_ARCH:${QE_TARGET_DIR}/bin/${EPICS_HOST_ARCH}:/usr/lib64/qt5/bin:${PATH}
		export LD_LIBRARY_PATH=${EPICS_BASE}/lib/${EPICS_HOST_ARCH}:/usr/local/qwt-6.1.3/lib:${QE_TARGET_DIR}/lib/${EPICS_HOST_ARCH}:${QE_TARGET_DIR}/lib/${EPICS_HOST_ARCH}/designer
		export QT_PLUGIN_PATH=${QT_PLUGIN_PATH}:${QWT_ROOT}/plugins:$QE_TARGET_DIR/lib/$EPICS_HOST_ARCH

	6. ``source .bashrc``
	7. To validate your setup, create a new project and open the designer, you should get qwt and epics qt widgets shown.


Clone the tomoScan DAQ system
------------------------------

.. note:: 
	
	Make sure that the python environment is activated before proceeding with this section.

------------------------------------------------------------------------------------


The scanning tool (BEATS_tomoscan) is available on github. The most recent version can be found on this link: https://github.com/SESAME-Synchrotron/BEATS_tomoscan.git. To clone and run, launch your terminal then do the follwoing:

	::

		$ cd /opt/epics/support
		$ git clone git@github.com:SESAME-Synchrotron/BEATS_tomoscan.git

	check configure/RELEASE all the epics directories are correct:
	::
		$ EPICS_BASE=/opt/epics/base
		$ SUPPORT=/opt/epics/support
		$ BUSY=$(SUPPORT)/busy
		$ AUTOSAVE=$(SUPPORT)/autosave
		$ ASYN=$(SUPPORT)/asyn

	Run the following commands on BEATS_tomoscan
	::
		$ make
		$ python setup.py install


Postrequisites
---------------

The following should be installed on the computer after installing the BEATS_tomoscan:

	* BEATS H5 Writer refer to:
	* PETRA/SED/BEATS/ sharing file system should be mounted on the local station.
	* BEATS_Dashboard refering to: :doc:`dashboard_install`
	* clone the SEDSS package to this directory as:
	::

		$ cd /${Home}/DAQ/SW/venv3.9/lib/python3.9/site-packages/tomoscan-0.1-py3.9.egg
		$ git clone git@github.com:SESAME-Synchrotron/SEDSS.git
