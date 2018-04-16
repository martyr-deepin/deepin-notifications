include(src/src.pri)

TEMPLATE = app
TARGET = deepin-notifications

QT += dbus widgets svg sql
CONFIG += c++11 link_pkgconfig
PKGCONFIG += dtkwidget gsettings-qt

SOURCES += src/main.cpp

RESOURCES += images.qrc

target.path = $${PREFIX}/lib/deepin-notifications
INSTALLS += target

service.input      = files/deepin-notification.service.in
service.output     = files/deepin-notification.service

QMAKE_SUBSTITUTES += service
QMAKE_CLEAN       += $${service.output} $${ddedbus.output}

service.path   = $${PREFIX}/lib/systemd/user/
service.files += files/deepin-notification.service
INSTALLS += service
