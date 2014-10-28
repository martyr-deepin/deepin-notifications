#include <QApplication>
#include "bubblemanager.h"
#include "notifications_dbus_adaptor.h"

int main(int argc, char *argv[])
{
    QApplication app(argc, argv);
    BubbleManager manager;
    NotificationsDBusAdaptor adapter(&manager);
    manager.registerAsService();

    return app.exec();
}
