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
#include <QTimer>
#include "bubble.h"
#include "dbuscontrol.h"
#include "dbus_daemon_interface.h"
#include "dbuslogin1manager.h"
#include "notificationentity.h"

#include "persistence.h"

#include <QDebug>


BubbleManager::BubbleManager(QObject *parent) :
    QObject(parent),
    m_persistence(new Persistence),
    m_dbusControlCenter(0)
{
    m_bubble = new Bubble();

    m_dbusDaemonInterface = new DBusDaemonInterface(DBusDaemonDBusService, DBusDaemonDBusPath,
                                                    QDBusConnection::sessionBus(), this);

    m_dbusdockinterface = new DBusDockInterface(DBbsDockDBusServer, DBusDockDBusPath,
                                                QDBusConnection::sessionBus(), this);

    m_login1ManagerInterface = new Login1ManagerInterface(Login1DBusService, Login1DBusPath,
                                                          QDBusConnection::systemBus(), this);

    m_dbusControlCenter = new DBusControlCenter(ControlCenterDBusService,
                                                    ControlCenterDBusPath,
                                                    QDBusConnection::sessionBus(),
                                                    this);

    connect(m_dbusDaemonInterface, SIGNAL(NameOwnerChanged(QString, QString, QString)),
            this, SLOT(dbusNameOwnerChangedSlot(QString, QString, QString)));

    connect(m_login1ManagerInterface, SIGNAL(PrepareForSleep(bool)),
            this, SLOT(onPrepareForSleep(bool)));

    connect(m_dbusdockinterface, &DBusDockInterface::geometryChanged, this, &BubbleManager::dockchangedSlot);
    connect(m_persistence, &Persistence::RecordAdded, this, &BubbleManager::AddOneRecord);
}

BubbleManager::~BubbleManager()
{

}

void BubbleManager::CloseNotification(uint id)
{
    bubbleDismissed(id);

    return;
}

QStringList BubbleManager::GetCapbilities()
{
    QStringList result;
    result << "action-icons" << "actions" << "body" << "body-hyperlinks" << "body-markup";

    return result;
}

QString BubbleManager::GetServerInformation(QString &name, QString &vender, QString &version)
{
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
#ifdef QT_DEBUG
    qDebug() << "Notify" << appName << appIcon << summary << body << actions << hints << expireTimeout;
#endif

    // timestamp as id;
    const qint64 id = QDateTime::currentMSecsSinceEpoch();
    NotificationEntity *notification = new NotificationEntity(appName, QString::number(id), appIcon, summary,
                                                              body, actions, hints, this);
    m_persistence->addOne(notification);
    m_entities.enqueue(notification);
    if (!m_bubble->isVisible()) { consumeEntities(); }

    return id;
}

QString BubbleManager::GetAllRecords()
{
    QJsonArray array;

    const QList<NotificationEntity> &value = m_persistence->getAll();
    for (const NotificationEntity &entity : value) {
        QJsonObject obj
        {
            {"name", entity.appName()},
            {"icon", entity.appIcon()},
            {"summary", entity.summary()},
            {"body", entity.body()},
            {"id", entity.id()}
        };
        array.append(obj);
    }

    QJsonDocument doc(array);
    return doc.toJson();
}

void BubbleManager::RemoveRecord(const QString &id)
{
    m_persistence->removeOne(id);
}

void BubbleManager::ClearRecords()
{
    m_persistence->removeAll();
}

void BubbleManager::AddOneRecord(NotificationEntity *entity)
{
    QJsonObject notifyJson
    {
        {"name", entity->appName()},
        {"icon", entity->appIcon()},
        {"summary", entity->summary()},
        {"body", entity->body()},
        {"id", entity->id()}
    };
    QJsonDocument doc(notifyJson);
    QString notify(doc.toJson(QJsonDocument::Compact));

    qDebug() << notifyJson;

    emit RecordAdded(notify);
}

void BubbleManager::registerAsService()
{
    QDBusConnection::sessionBus().registerService(NotificationsDBusService);
    QDBusConnection::sessionBus().registerObject(NotificationsDBusPath, this);
}

void BubbleManager::controlCenterRectChangedSlot(const QRect &rect)
{
    m_dccX = rect.x();
    QDesktopWidget *m_desktop = QApplication::desktop();
    QRect primaryRect = m_desktop->availableGeometry(m_desktop->primaryScreen());

    if (primaryRect.x() + primaryRect.width() - ControlCenterWidth < m_dccX
            && m_dccX < primaryRect.x() + primaryRect.width())
    {
        m_bubble->setBasePosition(getX(), getY());
    }
}

void BubbleManager::bubbleExpired(int id)
{
    qDebug() << "bubbleExpired";

    m_bubble->setVisible(false);
    emit NotificationClosed(id, BubbleManager::Expired);

    consumeEntities();
}

void BubbleManager::bubbleDismissed(int id)
{
    qDebug() << "bubbleDismissed";

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

bool BubbleManager::checkDockExistence()
{
    return m_dbusDaemonInterface->NameHasOwner(DBbsDockDBusServer).value();
}

bool BubbleManager::checkControlCenterExistence()
{
    return m_dbusDaemonInterface->NameHasOwner(ControlCenterDBusService).value();
}

int BubbleManager::getX()
{
    QDesktopWidget *desktop = QApplication::desktop();
    int pointerScreen = desktop->screenNumber(QCursor::pos());
    int primaryScreen = desktop->primaryScreen();

    if (pointerScreen != primaryScreen) {
        QRect rect( desktop->screenGeometry(pointerScreen) );
        return  rect.x() + rect.width();
    }

    QRect rect( desktop->screenGeometry(primaryScreen) );
    if (m_dockGeometry.width() < m_dockGeometry.height()) { // vertical
        if (m_dockGeometry.center().x() < rect.center().x()) { // left

        } else { // right
            return m_dccX - m_dockGeometry.width();
        }
    } else { // horizontal
        if (m_dockGeometry.center().y() < rect.center().y()) { // top

        } else { // bottom

        }
    }

    return m_dccX;
}

int BubbleManager::getY()
{
    QDesktopWidget *desktop = QApplication::desktop();
    int pointerScreen = desktop->screenNumber(QCursor::pos());
    int primaryScreen = desktop->primaryScreen();

    if (pointerScreen != primaryScreen) {
        QRect rect( desktop->screenGeometry(pointerScreen) );
        return  rect.y();
    }

    QRect rect( desktop->screenGeometry(primaryScreen) );
    if (m_dockGeometry.width() < m_dockGeometry.height()) { // vertical
        if (m_dockGeometry.center().x() < rect.center().x()) { // left

        } else { // right

        }
    } else { // horizontal
        if (m_dockGeometry.center().y() < rect.center().y()) { // top
            if ((rect.width() - m_dockGeometry.width()) / 2.0 > m_bubble->width()) {
                return rect.y() + m_dockGeometry.height();
            }
        } else { // bottom

        }
    }

    return rect.y();
}

int BubbleManager::getControlCenterX()
{
    return m_dbusControlCenter->rect().x();
}

void BubbleManager::dockchangedSlot(const QRect &geometry)
{
    m_dockGeometry = geometry;
    m_bubble->setBasePosition(getX(), getY());
}

void BubbleManager::dbusNameOwnerChangedSlot(QString name, QString, QString newName)
{
    QDesktopWidget *desktop = QApplication::desktop();
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
    if (!m_dbusControlCenter) {
        m_dbusControlCenter = new DBusControlCenter(ControlCenterDBusService,
                                                        ControlCenterDBusPath,
                                                        QDBusConnection::sessionBus(),
                                                        this);
    }
    connect(m_dbusControlCenter, &DBusControlCenter::rectChanged, this, &BubbleManager::controlCenterRectChangedSlot);

    m_dccX = getControlCenterX();
}

void BubbleManager::consumeEntities()
{
    qDebug() << "consumeEntities, entity length: " << m_entities.length();

    if (m_entities.isEmpty()) { return; }

    NotificationEntity *notification = m_entities.dequeue();
    m_bubble->setupPosition();

    QDesktopWidget *desktop = QApplication::desktop();
    int pointerScreen = desktop->screenNumber(QCursor::pos());
    int primaryScreen = desktop->primaryScreen();

    if (checkDockExistence()) {
        m_dockGeometry = m_dbusdockinterface->geometry();
    }

    if (checkControlCenterExistence() && pointerScreen == primaryScreen) {
        bindControlCenterX();
    } else {
        QWidget *pScreenWidget = desktop->screen(primaryScreen);
        m_dccX = pScreenWidget->x() + pScreenWidget->width();
    }

    qDebug() << m_dockGeometry << m_dccX << getX() << getY() ;
    m_bubble->setBasePosition(getX(), getY());
    m_bubble->setEntity(notification);

    m_bubble->disconnect();
    connect(m_bubble, SIGNAL(expired(int)), this, SLOT(bubbleExpired(int)));
    connect(m_bubble, SIGNAL(dismissed(int)), this, SLOT(bubbleDismissed(int)));
    connect(m_bubble, SIGNAL(replacedByOther(int)), this, SLOT(bubbleReplacedByOther(int)));
    connect(m_bubble, SIGNAL(actionInvoked(int, QString)), this, SLOT(bubbleActionInvoked(int, QString)));
    connect(m_bubble, SIGNAL(aboutToQuit()), this, SLOT(bubbleAboutToQuit()));

}