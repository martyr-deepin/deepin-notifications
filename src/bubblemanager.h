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

class PropertiesInterface;
class DBusDaemonInterface;
class BubbleManager : public QObject
{
    Q_OBJECT
public:
    explicit BubbleManager(QObject *parent = 0);
    ~BubbleManager();

    enum ClosedReason {
        Expired,
        Dismissed,
        Closed,
        Unknown
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

private:
    int m_counter;
    QTimer *m_quitTimer;
    Bubble *m_bubble;
    QQueue<NotificationEntity*> m_entities;
    PropertiesInterface *m_propertiesInterface;
    DBusDaemonInterface *m_dbusDaemonInterface;

    bool checkControlCenterExistence();
    int getControlCenterX();
    void bindControlCenterX();
    void consumeEntities();
};

#endif // BUBBLEMANAGER_H
