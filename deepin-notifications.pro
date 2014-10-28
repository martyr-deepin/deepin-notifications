TEMPLATE = subdirs
SUBDIRS = src

service.input      = files/org.freedesktop.Notifications.service.in
service.output     = files/org.freedesktop.Notifications.service
QMAKE_SUBSTITUTES += service
QMAKE_CLEAN       += $${service.output}

service.path   = $${PREFIX}/share/dbus-1/services
service.files += files/org.freedesktop.Notifications.service
INSTALLS += service
