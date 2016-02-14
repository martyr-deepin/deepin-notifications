/**
 * Copyright (C) 2014 Deepin Technology Co., Ltd.
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3 of the License, or
 * (at your option) any later version.
 **/

#ifndef BUBBLE_H
#define BUBBLE_H

#include <QQuickView>

class NotificationEntity;
class Bubble : public QQuickView
{
    Q_OBJECT
public:
    Bubble(NotificationEntity *entity=0);

    void setXBasePosition(int);
    void setupPosition();

    NotificationEntity *entity() const;
    void setEntity(NotificationEntity *entity);

public slots:
    QPoint getCursorPos();
    void setMask(int, int, int, int);

private:
    NotificationEntity *m_entity;
    void updateContent();
};

#endif // BUBBLE_H
