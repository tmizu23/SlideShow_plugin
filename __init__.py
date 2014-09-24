# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SlideShow
                                 A QGIS plugin
 This Plugin is SlideShow
                             -------------------
        begin                : 2014-09-20
        copyright            : (C) 2014 by Takayuki Mizutani
        email                : mizutani.takayuki+slideshow@gmai.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load SlideShow class from file SlideShow.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .slide_show import SlideShow
    return SlideShow(iface)
