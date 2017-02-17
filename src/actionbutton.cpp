#include <QPainter>
#include <QPainterPath>
#include <QMouseEvent>
#include <QMoveEvent>
#include <QtMath>
#include <QDebug>

#include "actionbutton.h"

static const QColor BorderColor = QColor::fromRgbF(0, 0, 0, 0.1);
static const QColor HoverColor = QColor(75, 184, 255);
static const QColor TextColor = QColor(0, 135, 255);
static const QColor TextHover = Qt::white;

ActionButton::ActionButton(QWidget *parent) :
    QFrame(parent)
{
    setMouseTracking(true);
    setFixedSize(70, 70);
}

bool ActionButton::addButton(QString id, QString text)
{
    if (m_buttons.length() > 1) return false;

    m_buttons.append(Button{id, text});
    update();

    return true;
}

bool ActionButton::isEmpty()
{
    return m_buttons.isEmpty();
}

void ActionButton::clear()
{
    m_buttons.clear();
}

void ActionButton::paintEvent(QPaintEvent *)
{
    if (m_buttons.isEmpty()) return;

    QPainter painter;
    painter.begin(this);

    painter.setPen(BorderColor);

    // draw left seperators
    painter.drawLine(rect().topLeft(), rect().bottomLeft());

    QPainterPath path;
    // draw two buttons
    if (m_buttons.length() > 1) {
        // draw background
        if (m_mouseInButtonOne) {
            path.moveTo(rect().topLeft());
            path.lineTo(width() - m_radius, 0);
            path.quadTo(QPoint(width(), 0), QPoint(width(), m_radius));
            path.lineTo(width(), height() / 2);
            path.lineTo(0, height() / 2);
            path.lineTo(rect().topLeft());
        } else if (m_mouseInButtonTwo) {
            path.moveTo(rect().bottomLeft());
            path.lineTo(width() - m_radius, height());
            path.quadTo(QPoint(width(), height()), QPoint(width(), height() - m_radius));
            path.lineTo(width(), height() / 2);
            path.lineTo(0, height() / 2);
        }
        painter.fillPath(path, HoverColor);
        painter.drawLine(QPoint(0, height() / 2), QPoint(width(), height() / 2));

        // draw text
        if (m_mouseHover) {
            painter.setPen(TextHover);
        } else {
            painter.setPen(TextColor);
        }
        painter.drawText(QRectF(rect().topLeft(), QSize(width(), height() / 2)),
                         Qt::AlignHCenter | Qt::AlignVCenter,
                         m_buttons.at(0).text);
        painter.drawText(QRectF(QPoint(0, height() / 2), QSize(width(), height() / 2)),
                         Qt::AlignHCenter | Qt::AlignVCenter,
                         m_buttons.at(1).text);
    } else { // draw one button
        // draw background
        if (m_mouseInButtonOne || m_mouseInButtonTwo) {
            path.moveTo(rect().topLeft());
            path.lineTo(width() - m_radius, 0);
            path.quadTo(QPoint(width(), 0), QPoint(width(), m_radius));
            path.lineTo(width(), height() - m_radius);
            path.quadTo(QPoint(width(), height()), QPoint(width() - m_radius, height()));
            path.lineTo(0, height());
            path.lineTo(rect().topLeft());

            painter.fillPath(path, HoverColor);
        }

        // draw text
        if (m_mouseHover) {
            painter.setPen(TextHover);
        } else {
            painter.setPen(TextColor);
        }
        painter.drawText(rect(),
                         Qt::AlignHCenter | Qt::AlignVCenter,
                         m_buttons.at(0).text);
    }

    painter.end();

    m_mouseInButtonOne = false;
    m_mouseInButtonTwo = false;
}

void ActionButton::mouseMoveEvent(QMouseEvent * event)
{
    if (event->y() < height() / 2) {
        m_mouseInButtonOne = true;
    } else {
        m_mouseInButtonTwo = true;
    }
    event->accept();
    m_mouseHover = true;
    update();
}

void ActionButton::mousePressEvent(QMouseEvent * event)
{
    if (event->y() < height() / 2) {
        m_mouseInButtonOne = true;
        emit buttonClicked(m_buttons.at(0).id);
    } else {
        m_mouseInButtonTwo = true;
        if (m_buttons.length() > 1) {
            emit buttonClicked(m_buttons.at(1).id);
        } else {
            emit buttonClicked(m_buttons.at(0).id);
        }
    }
    event->accept();
}

void ActionButton::leaveEvent(QEvent * event)
{
    m_mouseInButtonOne = false;
    m_mouseInButtonTwo = false;
    event->accept();
    m_mouseHover = false;

    update();
}
