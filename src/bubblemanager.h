/**
 * Copyright (C) 2014 Deepin Technology Co., Ltd.
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3 of the License, or
 * (at your option) any later version.
 **/

#ifndef BUBBLEMANAGER_H
#define BUBBLEMANAGER_H

#include <QObject>
#include <QStringList>
#include <QVariantMap>
#include <QQueue>
#include "bubble.h"

static const QString ControlCenterDBusService = "com.deepin.dde.ControlCenter";
static const QString ControlCenterDBusPath = "/com/deepin/dde/ControlCenter";
static const QString DBusDaemonDBusService = "org.freedesktop.DBus";
static const QString DBusDaemonDBusPath = "/org/freedesktop/DBus";
static const QString NotificationsDBusService = "org.freedesktop.Notifications";
static const QString NotificationsDBusPath = "/org/freedesktop/Notifications";
static const QString Login1DBusService = "org.freedesktop.login1";
static const QString Login1DBusPath = "/org/freedesktop/login1";

class PropertiesInterface;
class DBusDaemonInterface;
class Login1ManagerInterface;
class BubbleManager : public QObject
{
    Q_OBJECT
public:
    explicit BubbleManager(QObject *parent = 0);
    ~BubbleManager();

    enum ClosedReason {
        Expired = 1,
        Dismissed = 2,
        Closed = 3,
        Unknown = 4
    };

signals:
    void ActionInvoked(uint, const QString &);
    void NotificationClosed(uint, uint);

public slots:
    // Notifications dbus implementation
    void CloseNotification(uint);
    QStringList GetCapbilities();
    QString GetServerInformation(QString &, QString &, QString &);
    uint Notify(const QString &, uint, const QString &, const QString &, const QString &, const QStringList &, const QVariantMap, int);

    void registerAsService();

    void controlCenterXChangedSlot(QString, QVariantMap, QStringList);
    void dbusNameOwnerChangedSlot(QString, QString, QString);

    void bubbleExpired(int);
    void bubbleDismissed(int);
    void bubbleReplacedByOther(int);
    void bubbleActionInvoked(int, QString);
    void bubbleAboutToQuit();

    void onPrepareForSleep(bool);

private:
    int m_counter;
    QTimer *m_quitTimer;
    Bubble *m_bubble;
    QQueue<NotificationEntity*> m_entities;
    PropertiesInterface *m_propertiesInterface;
    DBusDaemonInterface *m_dbusDaemonInterface;
    Login1ManagerInterface *m_login1ManagerInterface;

    bool checkControlCenterExistence();
    int getControlCenterX();
    void bindControlCenterX();
    void consumeEntities();
};

#endif // BUBBLEMANAGER_H
