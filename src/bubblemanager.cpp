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
    m_propertiesInterface(0)
{
    m_bubble = new Bubble();

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

BubbleManager::~BubbleManager()
{
    m_bubble->rootObject()->disconnect();
    m_bubble->deleteLater();
}

void BubbleManager::CloseNotification(uint)
{
    m_quitTimer->start();

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
    emit ActionInvoked(id, actionId);
}

void BubbleManager::bubbleAboutToQuit()
{
    consumeEntities();
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

void BubbleManager::consumeEntities()
{
    if (m_entities.isEmpty()) return;
    m_quitTimer->stop();

    NotificationEntity *notification = m_entities.dequeue();
    m_bubble->setupPosition();

    if (checkControlCenterExistence()) {
        bindControlCenterX();
        m_bubble->setXBasePosition(getControlCenterX());
    }
    m_bubble->setEntity(notification);
    m_bubble->show();

    m_bubble->rootObject()->disconnect();
    connect(m_bubble->rootObject(), SIGNAL(expired(int)), this, SLOT(bubbleExpired(int)));
    connect(m_bubble->rootObject(), SIGNAL(dismissed(int)), this, SLOT(bubbleDismissed(int)));
    connect(m_bubble->rootObject(), SIGNAL(replacedByOther(int)), this, SLOT(bubbleReplacedByOther(int)));
    connect(m_bubble->rootObject(), SIGNAL(actionInvoked(int, QString)), this, SLOT(bubbleActionInvoked(int,QString)));
    connect(m_bubble->rootObject(), SIGNAL(aboutToQuit()), this, SLOT(bubbleAboutToQuit()));
}
