include(src/src.pri)

TEMPLATE = app
TARGET = deepin-notifications

QT += dbus widgets svg sql
CONFIG += c++11 link_pkgconfig
PKGCONFIG += dtkwidget gsettings-qt dframeworkdbus

SOURCES += src/main.cpp

RESOURCES += images.qrc

isEmpty(PREFIX){
    PREFIX = /usr
}

target.path = $${PREFIX}/lib/deepin-notifications

orgDBus.input = files/com.deepin.dde.freedesktop.Notification.service.in
orgDBus.output = files/com.deepin.dde.freedesktop.Notification.service

ddeDBus.input = files/com.deepin.dde.Notification.service.in
ddeDBus.output = files/com.deepin.dde.Notification.service

QMAKE_SUBSTITUTES += service orgDBus ddeDBus
QMAKE_CLEAN       += $${orgDBus.output} $${ddeDBus.output}

dbus.path = $${PREFIX}/share/dbus-1/services/
dbus.files += files/com.deepin.dde.freedesktop.Notification.service
dbus.files += files/com.deepin.dde.Notification.service

INSTALLS += target dbus
