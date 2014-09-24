# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SlideShow
                                 A QGIS plugin
 This Plugin is SlideShow
                              -------------------
        begin                : 2014-09-20
        git sha              : $Format:%H$
        copyright            : (C) 2014 by Takayuki Mizutani
        email                : mizutani.takayuki+slideshow@gmai.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, Qt
from PyQt4.QtGui import QAction, QIcon, QMessageBox, QToolBar, QDockWidget
# Initialize Qt resources from file resources.py
import resources_rc 

import os.path,sys,subprocess
from qgis.core import *
from qgis.gui import QgsMapTool

objs = []
slidepos=[]
slidelayer=[]
slidenum = 0

class SlideKeyEvent(QgsMapTool):   
    def __init__(self, canvas,iface):
        QgsMapTool.__init__(self, canvas)
        self.canvas = canvas
        self.iface = iface

    def setSlide(self):
        try: 
           legend = self.iface.legendInterface()
           for layer in legend.layers():
              legend.setLayerVisible(layer, False)
           for l in slidelayer[slidenum]:   
              for layer in legend.layers():
                 layerName = layer.originalName()
                 if layerName == l:
                    legend.setLayerVisible(layer, True)
                    break
           self.canvas.setExtent(slidepos[slidenum])
           self.canvas.refresh()
        except:
           pass
           
    def keyPressEvent(self, event):
        global slidenum
        #QMessageBox.information(None, "DEBUG:", str(slidenum))
        if event.key() == Qt.Key_Escape:
           for obj in objs:
               obj.setVisible(True)
               #print obj.objectName()    
           self.iface.mainWindow().showNormal()
           self.iface.mainWindow().showMaximized()
           self.canvas.unsetMapTool(self)           
           return
           
        if event.key() == 44:
           slidenum=slidenum-1
           if slidenum < 0: slidenum=len(slidepos)-1 
        elif event.key() == 46:
           slidenum=slidenum+1
           if slidenum == len(slidepos): slidenum=0
        elif 0 <= event.key() - 49 < len(slidepos):
           slidenum = event.key()-49
        
        self.setSlide()
        
class SlideShow:
    """QGIS Plugin Implementation."""
    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            '{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)


        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Slide Show')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'SlideShow')
        self.toolbar.setObjectName(u'SlideShow')
        
        self.slidelist = self.plugin_dir + os.sep +'slidelist.txt'

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('SlideShow', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
  

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/SlideShow/play.png'
        self.add_action(
            icon_path,
            text=self.tr(u'SlideShow'),
            callback=self.play,
            parent=self.iface.mainWindow())
        icon_path = ':/plugins/SlideShow/add.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Add Slide'),
            callback=self.add,
            parent=self.iface.mainWindow())
        icon_path = ':/plugins/SlideShow/list.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Slide List'),
            callback=self.list,
            parent=self.iface.mainWindow())
        icon_path = ':/plugins/SlideShow/info.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Information'),
            callback=self.info,
            parent=self.iface.mainWindow())

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Slide Show'),
                action)
            self.iface.removeToolBarIcon(action)
#        QMessageBox.information(None, "DEBUG:", "debug message") 

        
    def info(self):
        html =self.tr(u"""
        <h1>SlideShow</h1>
        <h2>Usage</h2>
        <ol>
        <li>Display the layer for the slide</li> 
        <li>[Add Slide] button, the map will be added to the slide list</li>
        <li>[Slide List] button, you can edit the slide setting or order by hand </li>
        <li>[SlideShow] button, the slideshow will be start</li>
        <li>Push the key.<br/>[ . ]  forward<br>[ , ]  back<br/>[ esc ]  stop <br/>[ 0-9 ]  jump</li>
        </ol>
        """)
        QMessageBox.information(None, "Information:", html)

    def list(self):
        if not os.path.exists(self.slidelist):
           QMessageBox.information(None, "Information:", self.tr(u"No Slide."))
           return
        if sys.platform == "win32":
           os.startfile(self.slidelist)
        else:
           subprocess.call(["open",self.slidelist])
        
    def add(self):
        reply = QMessageBox.question(None, "Message:", self.tr(u"Do you want to add to the slide this map ?"),QMessageBox.Yes,QMessageBox.No)
        if reply == QMessageBox.Yes:
           f = open(self.slidelist, 'a+')
           rect = self.iface.mapCanvas().extent()
           area =[str(rect.xMinimum()),str(rect.yMinimum()),str(rect.xMaximum()),str(rect.yMaximum())]
           allLayers = self.iface.mapCanvas().layers()
           l = [i.originalName().encode('utf-8') for i in allLayers]
           f.write(','.join(area) + "," + ','.join(l) + "\r\n")
           f.flush()
           f.close()
           
       
    def play(self):
        global slidenum
        if not os.path.exists(self.slidelist):
           QMessageBox.information(None, "Information:", self.tr(u"No Slide."))
           return
        f = open(self.slidelist, 'rU')
        for r in f:
           d = r.strip().rstrip("\r\n").split(',')
           if d[0]!="":
              slidepos.append(QgsRectangle(float(d[0]),float(d[1]),float(d[2]),float(d[3])))
              slidelayer.append(d[4:])
        f.close()
    
        ske = SlideKeyEvent(self.iface.mapCanvas(),self.iface)
        self.iface.mapCanvas().setMapTool(ske)
       
        toolbars = self.iface.mainWindow().findChildren(QToolBar)
        panels = self.iface.mainWindow().findChildren(QDockWidget)
        

        for obj in toolbars + panels: 
           if obj.isVisible():
              objs.append(obj)
              obj.setVisible(False)

        self.iface.mainWindow().showFullScreen()
        self.iface.mapCanvas().setFocus()
        ske.setSlide()