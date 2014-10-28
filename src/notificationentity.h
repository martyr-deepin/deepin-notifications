#ifndef NOTIFICATIONENTITY_H
#define NOTIFICATIONENTITY_H

#include <QObject>
#include <QStringList>
#include <QVariantMap>

class NotificationEntity : public QObject
{
    Q_OBJECT
public:
    NotificationEntity(const QString &appName, uint id,
                       const QString &appIcon, const QString &summary,
                       const QString &body, const QStringList &actions,
                       const QVariantMap hints, int expireTimeout, QObject *parent=0);

    QString appName() const;
    void setAppName(const QString &appName);

    quint32 id() const;
    void setId(const quint32 &id);

    QString appIcon() const;
    void setAppIcon(const QString &appIcon);

    QString summary() const;
    void setSummary(const QString &summary);

    QString body() const;
    void setBody(const QString &body);

    QStringList actions() const;
    void setActions(const QStringList &actions);

    QVariantMap hints() const;
    void setHints(const QVariantMap &hints);

    int expireTimeout() const;
    void setExpireTimeout(int expireTimeout);

private:
    QString m_appName;
    quint32 m_id;
    QString m_appIcon;
    QString m_summary;
    QString m_body;
    QStringList m_actions;
    QVariantMap m_hints;
    int m_expireTimeout;
};

#endif // NOTIFICATIONENTITY_H
