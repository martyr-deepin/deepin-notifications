TEMPLATE = subdirs
SUBDIRS = src

service.input      = files/com.deepin.Notifications.service.in
service.output     = files/com.deepin.Notifications.service
QMAKE_SUBSTITUTES += service
QMAKE_CLEAN       += $${service.output}

service.path   = $${PREFIX}/share/dbus-1/services
service.files += files/com.deepin.Notifications.service
INSTALLS += service
