include(src/src.pri)

TEMPLATE = app
TARGET = deepin-notifications

QT += dbus widgets svg sql
CONFIG += c++11 link_pkgconfig
PKGCONFIG += dtkwidget gsettings-qt

SOURCES += src/main.cpp

RESOURCES += images.qrc

target.path = $${PREFIX}/lib/deepin-notifications

service.input      = files/deepin-notification.service.in
service.output     = files/deepin-notification.service

orgDBus.input = files/com.deepin.dde.freedesktop.Notification.service.in
orgDBus.output = files/com.deepin.dde.freedesktop.Notification.service

ddeDBus.input = files/com.deepin.dde.Notification.service.in
ddeDBus.output = files/com.deepin.dde.Notification.service

QMAKE_SUBSTITUTES += service orgDBus ddeDBus
QMAKE_CLEAN       += $${service.output} $${orgDBus.output} $${ddeDBus.output}

service.path   = $${PREFIX}/lib/systemd/user/
service.files += files/deepin-notification.service

dbus.path = $${PREFIX}/share/dbus-1/services/
dbus.files += files/com.deepin.dde.freedesktop.Notification.service
dbus.files += files/com.deepin.dde.Notification.service

INSTALLS += service target dbus
