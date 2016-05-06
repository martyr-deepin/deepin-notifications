include(src/src.pri)

TEMPLATE = app
TARGET = deepin-notifications

QT += qml quick dbus widgets svg
CONFIG += c++11 link_pkgconfig
PKGCONFIG += dtkbase dtkwidget gtk+-2.0

SOURCES += src/main.cpp

RESOURCES += images.qrc

target.path = $${PREFIX}/lib/deepin-notifications
INSTALLS += target

service.input      = files/com.deepin.Notifications.service.in
service.output     = files/com.deepin.Notifications.service
QMAKE_SUBSTITUTES += service
QMAKE_CLEAN       += $${service.output}

service.path   = $${PREFIX}/share/dbus-1/services
service.files += files/com.deepin.Notifications.service
INSTALLS += service
