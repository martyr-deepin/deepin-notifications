include(src/src.pri)

TEMPLATE = app
TARGET = deepin-notifications

QT += dbus widgets svg sql
CONFIG += c++11 link_pkgconfig
PKGCONFIG += dtkwidget

SOURCES += src/main.cpp

RESOURCES += images.qrc

target.path = $${PREFIX}/lib/deepin-notifications
INSTALLS += target

service.input      = files/com.deepin.Notifications.service.in
service.output     = files/com.deepin.Notifications.service

ddedbus.input = files/com.deepin.dde.Notification.service.in
ddedbus.output     = files/com.deepin.dde.Notification.service

QMAKE_SUBSTITUTES += service ddedbus
QMAKE_CLEAN       += $${service.output} $${ddedbus.output}

service.path   = $${PREFIX}/share/dbus-1/services
service.files += files/com.deepin.Notifications.service files/com.deepin.dde.Notification.service
INSTALLS += service
