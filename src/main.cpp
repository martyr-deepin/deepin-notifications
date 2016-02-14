/**
 * Copyright (C) 2014 Deepin Technology Co., Ltd.
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3 of the License, or
 * (at your option) any later version.
 **/

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
