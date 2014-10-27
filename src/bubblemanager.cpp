#include "bubblemanager.h"
#include <QStringList>
#include <QVariantMap>
#include <QQuickItem>
#include <QTimer>
#include <QApplication>
#include "bubble.h"
#include "properties_dbus_interface.h"
#include "dbus_daemon_interface.h"
#include "notificationentity.h"
#include <QDebug>

BubbleManager::BubbleManager(QObject *parent) :
    QObject(parent),
    m_counter(0),
    m_bubbles(QMap<quint32, Bubble*>()),
    m_propertiesInterface(0)
{
    m_quitTimer = new QTimer(this);
    m_quitTimer->setSingleShot(false);
    m_quitTimer->setInterval(1000 * 10);
    connect(m_quitTimer, SIGNAL(timeout()), QApplication::instance(), SLOT(quit()));
    m_dbusDaemonInterface = new DBusDaemonInterface(DBusDaemonDBusService,
                                                    DBusDaemonDBusPath,
                                                    QDBusConnection::sessionBus(),
                                                    this);
    connect(m_dbusDaemonInterface, SIGNAL(NameOwnerChanged(QString,QString,QString)),
            this, SLOT(dbusNameOwnerChangedSlot(QString,QString,QString)));
}

void BubbleManager::CloseNotification(uint)
{
    checkBubblesToQuit();
    return;
}

QStringList BubbleManager::GetCapbilities()
{
    QStringList result;
    result << "action-icons" << "actions" << "body" << "body-hyperlinks" << "body-markup";

    checkBubblesToQuit();
    return result;
}

QString BubbleManager::GetServerInformation(QString &name, QString &vender, QString &version)
{
    name = QString("DeepinNotifications");
    vender = QString("Deepin");
    version = QString("2.0");

    checkBubblesToQuit();
    return QString("1.2");
}

uint BubbleManager::Notify(const QString &appName, uint,
                           const QString &appIcon, const QString &summary,
                           const QString &body, const QStringList &actions,
                           const QVariantMap hints, int expireTimeout)
{
    qDebug() << "Notify" << appName << appIcon << summary << body << actions << hints << expireTimeout;

    m_quitTimer->stop();
    quint32 count = m_counter++;

    NotificationEntity *notification = new NotificationEntity(appName, count, appIcon, summary,
                                                              body, actions, hints, expireTimeout, this);

    Bubble *bubble = getBubble();
    bubble->setEntity(notification);
    bubble->setupPosition();
    m_bubbles[notification->id()] = bubble;

    if (checkControlCenterExistence()) {
        bindControlCenterX();
        bubble->setXBasePosition(getControlCenterX());
    }
    bubble->show();

    connect(bubble->rootObject(), SIGNAL(expired(int)), this, SLOT(bubbleExpired(int)));
    connect(bubble->rootObject(), SIGNAL(dismissed(int)), this, SLOT(bubbleDismissed(int)));
    connect(bubble->rootObject(), SIGNAL(actionInvoked(int, QString)), this, SLOT(bubbleActionInvoked(int,QString)));

    return count;
}

void BubbleManager::registerAsService()
{
    QDBusConnection::sessionBus().registerService(NotificationsDBusService);
    QDBusConnection::sessionBus().registerObject(NotificationsDBusPath, this);
}

void BubbleManager::bubbleExpired(int id)
{
    emit NotificationClosed(id, BubbleManager::Expired);

    Bubble *bubble = m_bubbles[id];
    bubble->deleteLater();
    m_bubbles.remove(id);
    checkBubblesToQuit();
}

void BubbleManager::bubbleDismissed(int id)
{
    emit NotificationClosed(id, BubbleManager::Dismissed);

    Bubble *bubble = m_bubbles[id];
    bubble->deleteLater();
    m_bubbles.remove(id);
    checkBubblesToQuit();
}

void BubbleManager::bubbleActionInvoked(int id, QString actionId)
{
    emit ActionInvoked(id, actionId);
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
            QMapIterator<quint32, Bubble*> iter(m_bubbles);
            while (iter.hasNext()) {
                iter.next();
                iter.value()->setXBasePosition(changedProperties["X"].toInt());
            }
        }
    }
}

void BubbleManager::dbusNameOwnerChangedSlot(QString name, QString, QString newName)
{
    if (name == ControlCenterDBusService) {
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

Bubble *BubbleManager::getBubble()
{
    QMapIterator<quint32, Bubble*> iter(m_bubbles);
    while (iter.hasNext()) {
        iter.next();
        if (iter.value()->isTransient()) {
            return iter.value();
        }
    }
    return new Bubble();
}

void BubbleManager::checkBubblesToQuit()
{
    if (m_bubbles.isEmpty()) {
        m_quitTimer->start();
    }
}
