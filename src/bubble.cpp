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
#include <QDesktopWidget>
#include <QApplication>
#include <QCursor>
#include <QLabel>
#include <QIcon>
#include <QTimer>
#include <QDebug>
#include <QPropertyAnimation>
#include <QParallelAnimationGroup>
#include "notificationentity.h"

DWIDGET_USE_NAMESPACE

static const QString BubbleStyleSheet = "QFrame#Background { "
                                        "background-color: rgba(0, 0, 0, 200);"
                                        "border-radius: 4px;"
                                        "border: solid 1px white;"
                                        "}"
                                        "QLabel#Title {"
                                        "font-size: 11px;"
                                        "color: rgba(255, 255, 255, 0.6);"
                                        "}"
                                        "QLabel#Body {"
                                        "font-size: 12px;"
                                        "color: white;"
                                        "}";

Bubble::Bubble(NotificationEntity *entity):
    QFrame(),
    m_entity(entity),
    m_background(new QFrame(this)),
    m_icon(new QLabel(m_background)),
    m_title(new QLabel(m_background)),
    m_body(new QLabel(m_background)),
    m_closeButton(new DImageButton(":/images/close.png", ":/images/close.png", ":/images/close.png", m_background))
{
    setWindowFlags(Qt::X11BypassWindowManagerHint | Qt::WindowStaysOnTopHint);
    setAttribute(Qt::WA_TranslucentBackground);

    initUI();
    initAnimations();
    initTimers();

    setupPosition();

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
    // TODO: remove the work-around paddings
    move(x - width() - 20, pos().y());
}

void Bubble::setupPosition()
{
    QDesktopWidget *desktop = QApplication::desktop();
    QRect pointerScreenRect = desktop->screen(desktop->screenNumber(QCursor::pos()))->geometry();
    setXBasePosition(pointerScreenRect.x() + pointerScreenRect.width());

    // TODO: remove the work-around paddings
    move(pos().x(), pointerScreenRect.y() + 20);
}

QPoint Bubble::getCursorPos()
{
    return QCursor::pos();
}

void Bubble::setMask(int x, int y, int width, int height)
{

}

void Bubble::closeButtonClicked()
{
    emit dismissed(int(m_entity->id()));

    m_outTimer->stop();
    m_aboutToOutTimer->stop();
}

void Bubble::mousePressEvent(QMouseEvent *)
{
    // TODO: default action support
    emit dismissed(int(m_entity->id()));

    m_outTimer->stop();
    m_aboutToOutTimer->stop();
}

void Bubble::updateContent()
{
    qDebug() << "updateContent";
    QString imagePath = m_entity->hints().contains("image-path") ? m_entity->hints()["image-path"].toString() : "";

    QJsonArray actions;
    foreach (QString action, m_entity->actions()) {
        actions.append(action);
    }

//    QJsonObject object;
//    object["id"] = int(m_entity->id());
//    object["app_name"] = m_entity->appName();
//    object["app_icon"] = m_entity->appIcon();
//    object["summary"] = m_entity->summary();
//    object["body"] = m_entity->body();
//    object["actions"] = actions;
//    object["image_path"] = imagePath;

    // TODO: all stuff in bubble.qml:updateContent
    m_outTimer->stop();
    m_aboutToOutTimer->stop();

    if (imagePath.isEmpty()) {
        // TODO: use gtk methods instead of QIcon.
        m_icon->setPixmap(QIcon::fromTheme(m_entity->appIcon()).pixmap(m_icon->size()));
    } else {
        m_icon->setPixmap(QPixmap(imagePath));
    }
    m_title->setText(m_entity->summary());
    m_body->setText(m_entity->body());

    if (!isVisible()) {
        setVisible(true);
        m_inAnimation->start();
    } else {
        m_background->move(m_inAnimation->endValue().toPoint());
    }
    m_aboutToOutTimer->start();
    m_outTimer->start();
}

void Bubble::initUI()
{
    setFixedSize(300, 70);
    setVisible(false);

    m_background->setObjectName("Background");
    m_background->setFixedSize(size());
    m_background->move(QPoint(0, -height()));

    m_icon->setFixedSize(48, 48);
    m_icon->move(11, 11);

    m_title->setObjectName("Title");
    m_title->setAlignment(Qt::AlignTop | Qt::AlignLeft);
    m_title->setFixedSize(230, 20);
    m_title->move(70, 6);

    m_body->setObjectName("Body");
    m_body->setAlignment(Qt::AlignTop | Qt::AlignLeft);
    m_body->setFixedSize(230, 40);
    m_body->move(70, 22);
    m_body->setWordWrap(true);

    m_closeButton->setFixedSize(10, 10);
    m_closeButton->move(width() - m_closeButton->width() - 4, 4);

    setStyleSheet(BubbleStyleSheet);

    connect(m_closeButton, &DImageButton::clicked, this, &Bubble::closeButtonClicked);
}

void Bubble::initAnimations()
{
    m_inAnimation = new QPropertyAnimation(m_background, "pos", this);
    m_inAnimation->setDuration(300);
    m_inAnimation->setStartValue(QPoint(0, -height()));
    m_inAnimation->setEndValue(QPoint(0, 0));
    m_inAnimation->setEasingCurve(QEasingCurve::OutCubic);

    m_outAnimation = new QParallelAnimationGroup(this);
    QPropertyAnimation *outPosAnimation = new QPropertyAnimation(m_background, "pos", this);
    outPosAnimation->setDuration(300);
    outPosAnimation->setStartValue(m_inAnimation->endValue());
    outPosAnimation->setEndValue(QPoint(width(), 0));
    outPosAnimation->setEasingCurve(QEasingCurve::OutCubic);
    QPropertyAnimation *outOpacityAnimation = new QPropertyAnimation(m_background, "opacity", this);
    outOpacityAnimation->setDuration(300);
    outOpacityAnimation->setStartValue(1.0);
    outOpacityAnimation->setEndValue(0);
    outOpacityAnimation->setEasingCurve(QEasingCurve::OutCubic);
    m_outAnimation->addAnimation(outPosAnimation);
    // TODO: opacity is not supported, use QGraphicsOpacityEffect
//    m_outAnimation->addAnimation(outOpacityAnimation);

    connect(m_outAnimation, &QParallelAnimationGroup::finished, [this]{
        emit expired(int(m_entity->id()));
    });
}

void Bubble::initTimers()
{
    m_outTimer = new QTimer(this);
    m_outTimer->setInterval(5000);
    m_outTimer->setSingleShot(true);
    connect(m_outTimer, &QTimer::timeout, [this]{
        if (containsMouse()) {
            m_outTimer->stop();
            m_outTimer->start();
        } else {
            m_outAnimation->start();
        }
    });

    m_aboutToOutTimer = new QTimer(this);
    m_aboutToOutTimer->setInterval(m_outTimer->interval() - 1000);
    m_aboutToOutTimer->setSingleShot(true);
    connect(m_aboutToOutTimer, &QTimer::timeout, this, &Bubble::aboutToQuit);
}

bool Bubble::containsMouse() const
{
    QRect rectToGlobal = QRect(mapToGlobal(rect().topLeft()),
                                mapToGlobal(rect().bottomRight()));
    return rectToGlobal.contains(QCursor::pos());
}
