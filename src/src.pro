TEMPLATE = app
TARGET = deepin-notifications

QT += qml quick dbus widgets

HEADERS += \
    bubble.h \
    bubblemanager.h \
    notifications_dbus_adaptor.h \
    properties_dbus_interface.h \
    dbus_daemon_interface.h \
    notificationentity.h

SOURCES += \
    main.cpp \
    bubble.cpp \
    bubblemanager.cpp \
    notifications_dbus_adaptor.cpp \
    properties_dbus_interface.cpp \
    dbus_daemon_interface.cpp \
    notificationentity.cpp

RESOURCES += qml.qrc images.qrc

# Additional import path used to resolve QML modules in Qt Creator's code model
QML_IMPORT_PATH =

target.path = $${PREFIX}/share/deepin-notifications
INSTALLS += target