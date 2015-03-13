from PyKDE4.kdeui import KGlobalSettings
from PyKDE4.kdecore import KConfig
from tempfile import mkstemp
from shutil import move
import os, sys, time, dbus

#
# Restart a D-Bus connected QApplication.
#
def _restart(service_id, binary):
  exited = False
  try:
    s = dbus.SessionBus()
    pd = s.get_object(service_id, '/MainApplication')
    pd.quit()
    exited = True
    time.sleep(0.5)
  except dbus.exceptions.DBusException:
    pass
  os.system(binary)
  return exited

#
# Change the color scheme to the file provided.
#
def scheme(schemeFile):
  '''Applies the color scheme to KDE globals'''
  scheme = KConfig(schemeFile)
  kdeglobals = KConfig('kdeglobals')
  for groupName in scheme.groupList():
    group = scheme.group(groupName)
    global_group = kdeglobals.group(groupName)
    for (k, v) in group.entryMap().items():
      global_group.writeEntry(k, v)
  kdeglobals.sync()
  KGlobalSettings.emitChange(KGlobalSettings.PaletteChanged)
  KGlobalSettings.emitChange(KGlobalSettings.StyleChanged)
  KGlobalSettings.emitChange(KGlobalSettings.SettingsChanged)
  s = dbus.SessionBus()
  _restart('org.kde.plasma-desktop', 'plasma-desktop')
  _restart('org.kde.krunner', 'krunner')
  time.sleep(3)

#
# Switch Yakuake's Konsole profiles.
#
def yakuakeProfile(value):
  s = dbus.SessionBus()
  new_yakuake = False
  try:
    y = s.get_object('org.kde.yakuake', '/MainApplication')
    y.quit()
    time.sleep(0.5)
    new_yakuake = True
  except dbus.exceptions.DBusException:
    pass
  yakuakerc = KConfig('yakuakerc')
  group = yakuakerc.group('Desktop Entry')
  group.writeEntry('DefaultProfile', value)
  yakuakerc.sync()
  konsolerc = KConfig('konsolerc')
  group = konsolerc.group('Desktop Entry')
  group.writeEntry('DefaultProfile', value)
  konsolerc.sync()
  os.system('yakuake')
  time.sleep(0.5)
  if new_yakuake:
    try:
      y = s.get_object('org.kde.yakuake', '/MainApplication')
      time.sleep(0.5)
      os.system('/home/nvmourik/.config/autostart/yakuake.sh')
      time.sleep(2)
    except dbus.exceptions.DBusException:
      pass

#
# Set a new plasma wallpaper
#
def wallpaper(value):
  tmpfile = '/tmp/plasmawallpaperscript.js'
  with open(tmpfile, 'w') as js:
    js.write("var wallpaper = '%s';\n" % value)
    js.write("var activity = activities()[0];\n")
    js.write("activity.currentConfigGroup = new Array('Wallpaper', 'image');\n")
    js.write("activity.writeConfig('wallpaper', wallpaper);\n")
    js.write("activity.writeConfig('userswallpaper', wallpaper);\n")
    js.write("activity.reloadConfig();\n")
  try:
    s = dbus.SessionBus()
    p = s.get_object('org.kde.plasma-desktop', '/App')
    p.loadScriptInInteractiveConsole(tmpfile)
    os.system('xdotool search --name "Desktop Shell Scripting Console" windowactivate key control+e control+w')
  except dbus.exceptions.DBusException:
    pass