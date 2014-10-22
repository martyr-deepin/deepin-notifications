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

    enum ClosedReason {
        Expired,
        Dismissed,
        Closed,
        Unknow
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
    void bubbleActionInvoked(int, QString);

private:
    int m_counter;
    QTimer *m_quitTimer;
    QMap<quint32, Bubble*> m_bubbles;
    PropertiesInterface *m_propertiesInterface;
    DBusDaemonInterface *m_dbusDaemonInterface;

    bool checkControlCenterExistence();
    int getControlCenterX();
    void bindControlCenterX();
    Bubble *getBubble();
    void checkBubblesToQuit();
};

#endif // BUBBLEMANAGER_H
