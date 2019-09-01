#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GdkPixbuf
import cairo
import os
import random
from xml.dom import minidom
import codecs
import base64

image_normal = "miku-a.png"
image_wink = "miku-b.png"

glade_xml = """
<?xml version="1.0" encoding="UTF-8"?>
<!-- Generated with glade 3.22.1 -->
<interface>
  <requires lib="gtk+" version="3.0"/>
  <object class="GtkWindow" id="WinkMiku">
    <property name="app_paintable">True</property>
    <property name="can_focus">True</property>
    <property name="events">GDK_EXPOSURE_MASK | GDK_POINTER_MOTION_MASK | GDK_POINTER_MOTION_HINT_MASK | GDK_BUTTON_MOTION_MASK | GDK_BUTTON1_MOTION_MASK | GDK_BUTTON2_MOTION_MASK | GDK_BUTTON3_MOTION_MASK | GDK_BUTTON_PRESS_MASK | GDK_BUTTON_RELEASE_MASK | GDK_KEY_PRESS_MASK | GDK_KEY_RELEASE_MASK | GDK_ENTER_NOTIFY_MASK | GDK_LEAVE_NOTIFY_MASK | GDK_FOCUS_CHANGE_MASK | GDK_STRUCTURE_MASK | GDK_PROPERTY_CHANGE_MASK | GDK_VISIBILITY_NOTIFY_MASK | GDK_PROXIMITY_IN_MASK | GDK_PROXIMITY_OUT_MASK | GDK_SUBSTRUCTURE_MASK | GDK_SCROLL_MASK</property>
    <property name="title" translatable="yes">ウィンクみく</property>
    <property name="resizable">True</property>
    <property name="skip_taskbar_hint">True</property>
    <property name="decorated">False</property>
    <signal name="button-press-event" handler="on_miku_button_press_event" swapped="no"/>
    <signal name="destroy" handler="on_WinkMiku_destroy" swapped="no"/>
    <signal name="draw" handler="on_WinkMiku_draw" swapped="no"/>
    <signal name="focus-in-event" handler="on_WinkMiku_focus_in_event" swapped="no"/>
    <signal name="focus-out-event" handler="on_WinkMiku_focus_out_event" swapped="no"/>
    <child>
      <placeholder/>
    </child>
    <child>
      <placeholder/>
    </child>
  </object>
  <object class="GtkMenu" id="menu">
    <property name="visible">True</property>
    <property name="can_focus">False</property>
    <child>
      <object class="GtkMenuItem" id="exit">
        <property name="visible">True</property>
        <property name="can_focus">False</property>
        <property name="label" translatable="yes">終了</property>
        <property name="use_underline">True</property>
        <signal name="activate" handler="on_exit_activate" swapped="no"/>
      </object>
    </child>
  </object>
</interface>
"""

class ConfigXML:
    OptionList = {   "x_pos":"0",
                     "y_pos":"0"
    }
    AppName = "WinkMiku"
    ConfigPath = "/.config/WinkMiku.xml"
    Options = {}    #オプション値の辞書
    domobj = None

    def __init__(self, read):
        #print "ConfigXML"
        if read == True:
            try:
                self.domobj = minidom.parse(os.path.abspath(os.path.expanduser("~") + self.ConfigPath))
                options = self.domobj.getElementsByTagName("options")
                for opt in options :
                    for op,defVal in self.OptionList.items():
                        elm = opt.getElementsByTagName(op)
                        if len(elm) > 0 :
                            self.Options[op] = self.getText(elm[0].childNodes)
                        else:
                            self.Options[op] = defVal
            except Exception as e:
                print(e)
                for op,defVal in self.OptionList.items():
                    self.Options[op] = defVal

    def getText(self,nodelist):
        rc = ""
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                text = str(node.data)
                text = text.rstrip(" \t\n")
                text = text.lstrip(" \t\n")
                rc = rc + text
        return rc

    def GetOption(self, optName ):
        if optName == "password":
            return str(base64.b64decode(self.Options[optName]))
        else:
            try:
                return str(self.Options[optName])
            except:
                return str(self.OptionList[optName])

    def SetOption(self, optName, value ):
        if optName == "password":
            val = base64.b64encode(value)
            self.Options[optName] = val
        else:
            self.Options[optName] = value

    def Write(self):
        try:
            impl = minidom.getDOMImplementation()
            newdoc = impl.createDocument(None, self.AppName, None)
            root = newdoc.documentElement
            opts = newdoc.createElement("options")
            root.appendChild(opts)
            for op in self.OptionList.keys():
                opt = newdoc.createElement(op)
                opts.appendChild(opt)
                text = newdoc.createTextNode(str(self.Options[op]))
                opt.appendChild(text)
            file = codecs.open(os.path.abspath(os.path.expanduser("~") + self.ConfigPath), 'wb', encoding='utf-8')
            newdoc.writexml(file, '', '\t', '\n', encoding='utf-8')
        except:
            print ("Error Config Write")

class Miku:

    timeout_interval = 1

    def __init__(self):
        """

        """
        conf = ConfigXML(True)
        self.wTree = Gtk.Builder()
        self.wTree.add_from_string(glade_xml)
        self.context_menu =  self.wTree.get_object ("menu")
        self.mainWindow = self.wTree.get_object ("WinkMiku")
        # GdkColormap to GdkVisual
        # なんか透過ウィンドウを作成するのはこれがミソっぽい
        screen = self.mainWindow.get_screen()
        visual = screen.get_rgba_visual()
        if visual != None and screen.is_composited():
            self.mainWindow.set_visual(visual)
        else:
            print ("no Composited...")
        dic = {
            "on_exit_activate" : self.on_WinkMiku_destroy,
            "on_WinkMiku_destroy" : self.on_WinkMiku_destroy,
            "on_WinkMiku_focus_in_event" : self.on_WinkMiku_focus_in_event,
            "on_WinkMiku_focus_out_event" : self.on_WinkMiku_focus_out_event,
            "on_miku_button_press_event" : self.on_miku_button_press_event,
            "on_WinkMiku_destroy_event" : self.on_WinkMiku_destroy_event,
            "on_WinkMiku_draw" : self.on_WinkMiku_draw
        }
        self.wTree.connect_signals(dic)
        self.inFocus = False
        self.image = cairo.ImageSurface.create_from_png(os.path.dirname(os.path.abspath(__file__))+"/" + image_normal)
        self.icon = 0
        self.timeout = GLib.timeout_add_seconds(int(self.timeout_interval),self.timeout_callback,self)
        xpos = conf.GetOption("x_pos")
        ypos = conf.GetOption("y_pos")
        # self.mainWindow.set_opacity(0.0)
        self.mainWindow.move(int(xpos),int(ypos))
        # リサイズしてからリサイズ禁止にする
        h = self.image.get_height()
        w = self.image.get_width()
        self.mainWindow.resize(w,h)
        self.mainWindow.resizable = False
        self.mainWindow.show_all()

    def on_miku_button_press_event(self,widget,event):
        print ("on_miku_button_press_event")
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:
            #右クリック
            self.context_menu.popup(None, None, None,None, event.button, event.time)

    def on_WinkMiku_focus_in_event(self,widget,event):
        print ("on_WinkMiku_focus_in_event")
        #self.mainWindow.set_decorated(True)
        self._saveConf()

    def on_WinkMiku_focus_out_event(self,widget,event):
        print ("on_WinkMiku_focus_out_event")
        #self.mainWindow.set_decorated(False)
        self._saveConf()

    def _changeIcon(self):
        self.icon = random.randint(0,15)
        if self.icon == 0:
            self.image = cairo.ImageSurface.create_from_png(os.path.dirname(os.path.abspath(__file__))+"/" + image_wink)
        else:
            self.image = cairo.ImageSurface.create_from_png(os.path.dirname(os.path.abspath(__file__))+"/" + image_normal)

    def timeout_callback(self,event):
        # print ("timeout_callback")
        self._changeIcon()
        self.mainWindow.queue_draw()
        return True

    def _saveConf(self):
        conf = ConfigXML(False)
        (xpos, ypos) = self.mainWindow.get_position()
        conf.SetOption("x_pos",xpos)
        conf.SetOption("y_pos",ypos)
        conf.Write()

    def on_WinkMiku_destroy_event(self,widget):
        self._saveConf()

    def on_WinkMiku_destroy(self,widget):
        Gtk.main_quit()

    def on_WinkMiku_draw(self, widget, cr):
        """
            cr is cairo.Context
        """
        print ("on_WinkMiku_draw")
        cr.set_source_rgba(1.0, 1.0, 1.0, 0.0)
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.set_source_surface(self.image, 0, 0)
        cr.paint()
       
if __name__ == '__main__':
    Miku()
    Gtk.main()
