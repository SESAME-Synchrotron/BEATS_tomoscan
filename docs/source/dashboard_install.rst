Installing BEATS Dashboard
===========================

This page includes information about the needed packages to run the BEATS Dashboard.

Prerequisites
--------------

The following should be installed on the computer before running the scanning tool:

* Linux redhat based OS (This work has been done under CentOS 7.4, however, there should be no reason to not work on other distributions)
* Python 3.9
* QT 4.1.0 based on 5.9.7. :ref:`Qt <dashboard_install#Qt-and-its-libraries>`
* Tomoscan refer to: :doc:`BEATS_install`
* tmux


Clone and run the BEATS dashboard
----------------------------------

The BEATS dashboard is available on github. The most recent version can be found on this link: https://github.com/SESAME-Synchrotron/BEATS_Dashboard.git. To clone and run, launch your terminal then do the follwoing:

::

	$ cd /home/control/DAQ/operation
	$ git clone git@github.com:SESAME-Synchrotron/BEATS_Dashboard.git
	open and build the project in ``qtcreator``
	$ cd /BEATS_Dashboard/BEATS_DAQ_Control_Monitor/
	$ make distclean
	$ qmake
	$ make
	$ BEATS_DAQ_Control_Monitor

.. warning:: If all is fine, you should see the GUI pops up; otherwise, an error occurred during the installation.

.. note:: Create the hosts names in ``/etc/hosts`` according to ``Scripts/BEATS_GUI_Bash_Start``.

.. note:: You have to check and edit the directories and hosts in the ``Scripts/`` folder according to your environment.
