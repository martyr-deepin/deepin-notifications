/**
 * Copyright (C) 2014 Deepin Technology Co., Ltd.
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3 of the License, or
 * (at your option) any later version.
 **/

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
    this->setFlags(Qt::X11BypassWindowManagerHint | Qt::WindowStaysOnTopHint);
    this->setColor(Qt::transparent);
    this->rootContext()->setContextProperty("_bubble", this);
    this->setSource(QUrl("qrc:///ui/bubble.qml"));
    this->setVisible(false);

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
    QRect pointerScreenRect = desktop->screen(desktop->screenNumber(QCursor::pos()))->geometry();
    this->setXBasePosition(pointerScreenRect.x() + pointerScreenRect.width());
    this->setY(pointerScreenRect.y());
}

QPoint Bubble::getCursorPos()
{
    return QCursor::pos();
}

void Bubble::setMask(int x, int y, int width, int height)
{
    QQuickView::setMask(QRegion(x, y, width, height));
}

void Bubble::updateContent()
{
    QString imagePath = m_entity->hints().contains("image-path") ? m_entity->hints()["image-path"].toString() : "";

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
