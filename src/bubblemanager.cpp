/**
 * Copyright (C) 2014 Deepin Technology Co., Ltd.
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3 of the License, or
 * (at your option) any later version.
 **/

#include "bubblemanager.h"
#include <QStringList>
#include <QVariantMap>
#include <QQuickItem>
#include <QTimer>
#include <QDesktopWidget>
#include <QApplication>
#include "bubble.h"
#include "properties_dbus_interface.h"
#include "dbus_daemon_interface.h"
#include "dbuslogin1manager.h"
#include "notificationentity.h"
#include <QDebug>

BubbleManager::BubbleManager(QObject *parent) :
    QObject(parent),
    m_counter(0),
    m_propertiesInterface(0)
{
    m_bubble = new Bubble();

    m_quitTimer = new QTimer(this);
    m_quitTimer->setSingleShot(false);
    m_quitTimer->setInterval(1000 * 100);
    m_quitTimer->start();
    connect(m_quitTimer, SIGNAL(timeout()), QApplication::instance(), SLOT(quit()));

    m_dbusDaemonInterface = new DBusDaemonInterface(DBusDaemonDBusService, DBusDaemonDBusPath,
                                                    QDBusConnection::sessionBus(), this);
    m_login1ManagerInterface = new Login1ManagerInterface(Login1DBusService, Login1DBusPath,
                                                          QDBusConnection::systemBus(), this),

    connect(m_dbusDaemonInterface, SIGNAL(NameOwnerChanged(QString,QString,QString)),
            this, SLOT(dbusNameOwnerChangedSlot(QString,QString,QString)));

    connect(m_login1ManagerInterface, SIGNAL(PrepareForSleep(bool)),
            this, SLOT(onPrepareForSleep(bool)));
}

BubbleManager::~BubbleManager()
{

}

void BubbleManager::CloseNotification(uint id)
{
    if (id != (uint)(m_counter - 1 )) {
        return;
    }

    bubbleDismissed(id);

    return;
}

QStringList BubbleManager::GetCapbilities()
{
    m_quitTimer->start();

    QStringList result;
    result << "action-icons" << "actions" << "body" << "body-hyperlinks" << "body-markup";

    return result;
}

QString BubbleManager::GetServerInformation(QString &name, QString &vender, QString &version)
{
    m_quitTimer->start();

    name = QString("DeepinNotifications");
    vender = QString("Deepin");
    version = QString("2.0");

    return QString("1.2");
}

uint BubbleManager::Notify(const QString &appName, uint,
                           const QString &appIcon, const QString &summary,
                           const QString &body, const QStringList &actions,
                           const QVariantMap hints, int expireTimeout)
{
    qDebug() << "Notify" << appName << appIcon << summary << body << actions << hints << expireTimeout;

    quint32 count = m_counter++;

    NotificationEntity *notification = new NotificationEntity(appName, count, appIcon, summary,
                                                              body, actions, hints, expireTimeout, this);
    m_entities.enqueue(notification);
    if (!m_bubble->isVisible()) consumeEntities();

    return count;
}

void BubbleManager::registerAsService()
{
    QDBusConnection::sessionBus().registerService(NotificationsDBusService);
    QDBusConnection::sessionBus().registerObject(NotificationsDBusPath, this);
}

void BubbleManager::bubbleExpired(int id)
{
    qDebug() << "bubbleExpired";
    m_quitTimer->start();
    m_bubble->setVisible(false);
    emit NotificationClosed(id, BubbleManager::Expired);

    consumeEntities();
}

void BubbleManager::bubbleDismissed(int id)
{
    qDebug() << "bubbleDismissed";
    m_quitTimer->start();
    m_bubble->setVisible(false);
    emit NotificationClosed(id, BubbleManager::Dismissed);

    consumeEntities();
}

void BubbleManager::bubbleReplacedByOther(int id)
{
    emit NotificationClosed(id, BubbleManager::Unknown);
}

void BubbleManager::bubbleActionInvoked(int id, QString actionId)
{
    m_quitTimer->start();
    m_bubble->setVisible(false);
    emit ActionInvoked(id, actionId);

    consumeEntities();
}

void BubbleManager::bubbleAboutToQuit()
{
    qDebug() << "bubble is about to quit";
    consumeEntities();
}

void BubbleManager::onPrepareForSleep(bool sleep)
{
    // workaround to avoid the "About to suspend..." notifications still
    // hanging there on restoring from sleep confusing users.
    if (!sleep) {
        qDebug() << "Quit on restoring from sleep.";
        qApp->quit();
    }
}

bool BubbleManager::checkControlCenterExistence()
{
    return m_dbusDaemonInterface->NameHasOwner(ControlCenterDBusService).value();
}

int BubbleManager::getControlCenterX()
{
     return m_propertiesInterface->Get(ControlCenterDBusService, "X").value().variant().toInt();
}

void BubbleManager::controlCenterXChangedSlot(QString interfaceName, QVariantMap changedProperties, QStringList)
{
    if (interfaceName == ControlCenterDBusService) {
        if (changedProperties.contains("X")) {
            m_bubble->setXBasePosition(changedProperties["X"].toInt());
        }
    }
}

void BubbleManager::dbusNameOwnerChangedSlot(QString name, QString, QString newName)
{
    QDesktopWidget * desktop = QApplication::desktop();
    int currentScreen = desktop->screenNumber(m_bubble->pos());
    int primaryScreen = desktop->primaryScreen();
    if (name == ControlCenterDBusService && currentScreen == primaryScreen) {
        if (!newName.isEmpty()) {
            bindControlCenterX();
        }
    }
}

void BubbleManager::bindControlCenterX()
{
    if (!m_propertiesInterface) {
        m_propertiesInterface = new PropertiesInterface(ControlCenterDBusService,
                                                        ControlCenterDBusPath,
                                                        QDBusConnection::sessionBus(),
                                                        this);
    }
    connect(m_propertiesInterface, SIGNAL(PropertiesChanged(QString,QVariantMap,QStringList)),
            this, SLOT(controlCenterXChangedSlot(QString,QVariantMap,QStringList)));
}

void BubbleManager::consumeEntities()
{
    qDebug() << "consumeEntities, entity length: " << m_entities.length();

    if (m_entities.isEmpty()) return;
    m_quitTimer->stop();

    NotificationEntity *notification = m_entities.dequeue();
    m_bubble->setupPosition();

    QDesktopWidget * desktop = QApplication::desktop();
    int pointerScreen = desktop->screenNumber(QCursor::pos());
    int primaryScreen = desktop->primaryScreen();

    if (checkControlCenterExistence() && pointerScreen == primaryScreen) {
        bindControlCenterX();
        m_bubble->setXBasePosition(getControlCenterX());
    }
    m_bubble->setEntity(notification);

    m_bubble->disconnect();
    connect(m_bubble, SIGNAL(expired(int)), this, SLOT(bubbleExpired(int)));
    connect(m_bubble, SIGNAL(dismissed(int)), this, SLOT(bubbleDismissed(int)));
    connect(m_bubble, SIGNAL(replacedByOther(int)), this, SLOT(bubbleReplacedByOther(int)));
    connect(m_bubble, SIGNAL(actionInvoked(int, QString)), this, SLOT(bubbleActionInvoked(int,QString)));
    connect(m_bubble, SIGNAL(aboutToQuit()), this, SLOT(bubbleAboutToQuit()));
}
