/*
 * Copyright (C) 2017 ~ 2018 Deepin Technology Co., Ltd.
 *
 * Author:     kirigaya <kirigaya@mkacg.com>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

#ifndef ACTIONBUTTON_H
#define ACTIONBUTTON_H

#include <QFrame>
#include <QPainter>

class ActionButton : public QFrame
{
    Q_OBJECT
    struct Button {
        QString id;
        QString text;
    };

public:
    ActionButton(QWidget * parent = 0);

    bool addButton(QString id, QString text);
    bool isEmpty();
    void clear();

signals:
    void buttonClicked(QString id);

protected:
    void paintEvent(QPaintEvent *) Q_DECL_OVERRIDE;
    void mouseMoveEvent(QMouseEvent *) Q_DECL_OVERRIDE;
    void mousePressEvent(QMouseEvent *) Q_DECL_OVERRIDE;
    void leaveEvent(QEvent *) Q_DECL_OVERRIDE;
    void mouseReleaseEvent(QMouseEvent *) Q_DECL_OVERRIDE;

private:
    int m_radius = 4;
    QList<Button> m_buttons;
    bool m_mouseInButtonOne = false;
    bool m_mouseInButtonTwo = false;
    bool m_mousePressed = false;
    bool m_mouseHover = false;
};

#endif // ACTIONBUTTON_H
