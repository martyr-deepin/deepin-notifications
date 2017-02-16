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
#include <QGraphicsDropShadowEffect>
#include <QPropertyAnimation>
#include <QParallelAnimationGroup>
#include "appicon.h"
#include "notificationentity.h"
#include "actionbutton.h"

#include <dplatformwindowhandle.h>
#include <anchors.h>
#include <denhancedwidget.h>

DWIDGET_USE_NAMESPACE

static const QString BubbleStyleSheet = "QFrame#Background { "
                                        "background-color: rgba(0, 0, 0, 180);"
                                        "border-radius: 6px;"
                                        "border: solid 1px white;"
                                        "}"
                                        "QLabel#Title {"
                                        "font-size: 11px;"
                                        "color: black;"
                                        "}"
                                        "QLabel#Body {"
                                        "font-size: 12px;"
                                        "color: black;"
                                        "}";
static const int ShadowWidth = 20;
static const int BubbleWidth = 300;
static const int BubbleHeight = 70;

Bubble::Bubble(NotificationEntity *entity):
    QFrame(),
    m_entity(entity),
    m_bgContainer(new QFrame(this)),
    m_background(new DBlurEffectWidget(this)),
    m_icon(new AppIcon(m_background)),
    m_title(new QLabel(m_background)),
    m_body(new QLabel(m_background)),
    m_actionButton(new ActionButton(m_background)),
    m_closeButton(new DImageButton(":/images/close.png", ":/images/close.png", ":/images/close.png", m_background))
{
    setWindowFlags(Qt::X11BypassWindowManagerHint | Qt::WindowStaysOnTopHint);
    setAttribute(Qt::WA_TranslucentBackground);

    m_background->setBlendMode(DBlurEffectWidget::BehindWindowBlend);
    m_background->setBlurRectXRadius(4);
    m_background->setBlurRectYRadius(4);
    m_background->setMaskColor(QColor(245, 245, 245));

    Anchors<DBlurEffectWidget> anchors_background(m_background);
    anchors_background.setCenterIn(m_bgContainer);

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


void Bubble::setBasePosition(int x,int y)
{
    move(x - width(), y);
}

void Bubble::setupPosition()
{
    QDesktopWidget *desktop = QApplication::desktop();
    QRect pointerScreenRect = desktop->screen(desktop->screenNumber(QCursor::pos()))->geometry();
    setBasePosition(pointerScreenRect.x() + pointerScreenRect.width(), pointerScreenRect.y());
}

QPoint Bubble::getCursorPos()
{
    return QCursor::pos();
}

void Bubble::setMask(int, int, int, int)
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
        m_icon->setIcon(m_entity->appIcon());
    } else {
        m_icon->setIcon(imagePath);
    }
    m_title->setText(m_entity->summary());
    m_body->setText(m_entity->body());

    processActions();

    if (!isVisible()) {
        setVisible(true);
        m_inAnimation->start();
    } else {
        m_bgContainer->move(m_inAnimation->endValue().toPoint());
    }
    m_aboutToOutTimer->start();
    m_outTimer->start();
}

void Bubble::initUI()
{
    setFixedSize(BubbleWidth + ShadowWidth * 2, BubbleHeight + ShadowWidth * 2);
    setVisible(false);

    m_bgContainer->setAttribute(Qt::WA_TranslucentBackground);
    m_bgContainer->setFixedSize(size());
    m_bgContainer->move(QPoint(0, -height()));

    m_background->setFixedSize(BubbleWidth, BubbleHeight);

    QFrame *bgShadow = new QFrame(m_bgContainer);
    bgShadow->setObjectName("Background");
    bgShadow->move(ShadowWidth, ShadowWidth);
    bgShadow->setFixedSize(m_background->size());

    QGraphicsDropShadowEffect *dropShadow = new QGraphicsDropShadowEffect;
    dropShadow->setColor(QColor::fromRgbF(0, 0, 0, 0.9));
    dropShadow->setBlurRadius(20);
    dropShadow->setOffset(2);
    m_bgContainer->setGraphicsEffect(dropShadow);

    m_icon->setFixedSize(48, 48);
    m_icon->move(11, 11);

    m_title->setTextFormat(Qt::RichText);
    m_title->setObjectName("Title");
    m_title->setAlignment(Qt::AlignTop | Qt::AlignLeft);
    m_title->move(70, 6);

    m_body->setTextFormat(Qt::RichText);
    m_body->setObjectName("Body");
    m_body->setAlignment(Qt::AlignTop | Qt::AlignLeft);
    m_body->move(70, 22);
    m_body->setWordWrap(true);

    m_actionButton->move(m_background->width() - m_actionButton->width(), 0);

    m_closeButton->setFixedSize(10, 10);
    m_closeButton->move(m_background->width() - m_closeButton->width() - 4, 4);

    setStyleSheet(BubbleStyleSheet);

    connect(m_closeButton, &DImageButton::clicked, this, &Bubble::closeButtonClicked);
    connect(m_actionButton, &ActionButton::buttonClicked, [this](QString actionId){
        emit actionInvoked(m_entity->id(), actionId);
    });
}

void Bubble::initAnimations()
{
    m_inAnimation = new QPropertyAnimation(m_bgContainer, "pos", this);
    m_inAnimation->setDuration(300);
    m_inAnimation->setStartValue(QPoint(0, -height()));
    m_inAnimation->setEndValue(QPoint(0, 0));
    m_inAnimation->setEasingCurve(QEasingCurve::OutCubic);

    m_outAnimation = new QParallelAnimationGroup(this);
    QPropertyAnimation *outPosAnimation = new QPropertyAnimation(m_bgContainer, "pos", this);
    outPosAnimation->setDuration(300);
    outPosAnimation->setStartValue(m_inAnimation->endValue());
    outPosAnimation->setEndValue(QPoint(width(), 0));
    outPosAnimation->setEasingCurve(QEasingCurve::OutCubic);
    QPropertyAnimation *outOpacityAnimation = new QPropertyAnimation(m_bgContainer, "opacity", this);
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

void Bubble::processActions()
{
    m_actionButton->clear();

    QString id;
    QString text;
    QStringList actions = m_entity->actions();
    for (int i = 0; i < actions.length(); i++) {
        if (i % 2 == 0) {
            id = actions.at(i);
            if (id == "default") {
                i++; continue;
            }
        } else {
            text = actions.at(i);
            m_actionButton->addButton(id, text);
        }
    }

    if (m_actionButton->isEmpty()) {
        m_title->setFixedSize(230, 20);
        m_body->setFixedSize(230, 40);
    } else {
        m_title->setFixedSize(160, 20);
        m_body->setFixedSize(160, 40);
    }
}
