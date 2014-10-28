TEMPLATE = app

QT += qml quick dbus widgets

HEADERS += \
    src/bubble.h \
    src/bubblemanager.h \
    src/notifications_dbus_adaptor.h \
    src/properties_dbus_interface.h \
    src/dbus_daemon_interface.h \
    src/notificationentity.h

SOURCES += src/main.cpp \
    src/bubble.cpp \
    src/bubblemanager.cpp \
    src/notifications_dbus_adaptor.cpp \
    src/properties_dbus_interface.cpp \
    src/dbus_daemon_interface.cpp \
    src/notificationentity.cpp

RESOURCES += qml.qrc \
    images.qrc

# Additional import path used to resolve QML modules in Qt Creator's code model
QML_IMPORT_PATH =

target.path = /usr/share/deepin-notifications
INSTALLS += target
