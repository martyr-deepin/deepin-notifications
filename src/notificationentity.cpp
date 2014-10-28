#include "notificationentity.h"

NotificationEntity::NotificationEntity(const QString &appName, uint id,
                                       const QString &appIcon, const QString &summary,
                                       const QString &body, const QStringList &actions,
                                       const QVariantMap hints, int expireTimeout, QObject *parent) :
    QObject(parent),
    m_appName(appName),
    m_id(id),
    m_appIcon(appIcon),
    m_summary(summary),
    m_body(body),
    m_actions(actions),
    m_hints(hints),
    m_expireTimeout(expireTimeout)
{
}
QString NotificationEntity::appName() const
{
    return m_appName;
}

void NotificationEntity::setAppName(const QString &appName)
{
    m_appName = appName;
}
quint32 NotificationEntity::id() const
{
    return m_id;
}

void NotificationEntity::setId(const quint32 &id)
{
    m_id = id;
}
QString NotificationEntity::appIcon() const
{
    return m_appIcon;
}

void NotificationEntity::setAppIcon(const QString &appIcon)
{
    m_appIcon = appIcon;
}
QString NotificationEntity::summary() const
{
    return m_summary;
}

void NotificationEntity::setSummary(const QString &summary)
{
    m_summary = summary;
}
QString NotificationEntity::body() const
{
    return m_body;
}

void NotificationEntity::setBody(const QString &body)
{
    m_body = body;
}
QStringList NotificationEntity::actions() const
{
    return m_actions;
}

void NotificationEntity::setActions(const QStringList &actions)
{
    m_actions = actions;
}
QVariantMap NotificationEntity::hints() const
{
    return m_hints;
}

void NotificationEntity::setHints(const QVariantMap &hints)
{
    m_hints = hints;
}
int NotificationEntity::expireTimeout() const
{
    return m_expireTimeout;
}

void NotificationEntity::setExpireTimeout(int expireTimeout)
{
    m_expireTimeout = expireTimeout;
}








