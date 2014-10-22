#include "bubble.h"
#include <QJsonObject>
#include <QJsonArray>
#include <QJsonDocument>
#include <QQuickItem>
#include <QDesktopWidget>
#include <QApplication>
#include <QCursor>
#include <QQmlContext>
#include "notificationentity.h"

Bubble::Bubble(NotificationEntity *entity):
    QQuickView(),
    m_entity(entity)
{
    this->setFlags(Qt::FramelessWindowHint | Qt::WindowStaysOnTopHint);
    this->setColor(Qt::transparent);
    this->rootContext()->setContextProperty("_bubble", this);
    this->setSource(QUrl("qrc:///src/ui/bubble.qml"));

    if(entity) this->updateContent();
}

NotificationEntity *Bubble::entity() const
{
    return m_entity;
}

void Bubble::setEntity(NotificationEntity *entity)
{
    m_entity = entity;
    this->updateContent();
}

void Bubble::setXBasePosition(int x)
{
    this->setX(x - this->width());
}

void Bubble::setupPosition()
{
    QDesktopWidget *desktop = QApplication::desktop();
    QRect primaryScreenRect = desktop->availableGeometry(desktop->primaryScreen());
    this->setXBasePosition(primaryScreenRect.x() + primaryScreenRect.width());
    this->setY(primaryScreenRect.y());
}

QPoint Bubble::getCursorPos()
{
    return QCursor::pos();
}

bool Bubble::isTransient()
{
    return true;
}

void Bubble::updateContent()
{
    QString imagePath = m_entity->hints()["image-path"].isNull() ? m_entity->hints()["image-path"].toString() : "";

    QJsonArray actions;
    foreach (QString action, m_entity->actions()) {
        actions.append(action);
    }

    QJsonObject object;
    object["id"] = int(m_entity->id());
    object["app_name"] = m_entity->appName();
    object["app_icon"] = m_entity->appIcon();
    object["summary"] = m_entity->summary();
    object["body"] = m_entity->body();
    object["actions"] = actions;
    object["image_path"] = imagePath;

    QJsonDocument doc(object);
    QMetaObject::invokeMethod(this->rootObject(), "updateContent", Q_ARG(QVariant, doc.toJson()));
}
