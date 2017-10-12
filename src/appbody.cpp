/*
 * Copyright (C) 2017 ~ 2017 Deepin Technology Co., Ltd.
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

#include "appbody.h"
#include <QPainter>
#include <QTextDocument>
#include <QVBoxLayout>
#include <QEvent>

static const QString DefaultCSS = "body { color: black; font-size: 11px; }";
static const QString HTMLTemplate = "<body>%1</body>";

AppBody::AppBody(QWidget *parent)
    : QWidget(parent)
{
    m_titleLbl = new QLabel;
    m_bodyLbl = new QLabel;

    m_bodyLbl->installEventFilter(this);

    QVBoxLayout *layout = new QVBoxLayout;
    layout->setMargin(0);
    layout->setSpacing(2);

    layout->addStretch();

    layout->addWidget(m_titleLbl);
    layout->addWidget(m_bodyLbl);

    layout->addStretch();

    setLayout(layout);
}

void AppBody::setTitle(const QString &title)
{
    m_title = title;

    m_titleLbl->setVisible(!title.isEmpty());

    m_titleLbl->setText(title);
}

void AppBody::setText(const QString &text)
{
    m_bodyText = text;

    m_bodyLbl->resize(width(), height() - m_titleLbl->height());

    m_bodyLbl->update();
}

bool AppBody::eventFilter(QObject *watched, QEvent *event)
{
    if (watched == m_bodyLbl && event->type() == QEvent::Paint) {
        QPainter painter(m_bodyLbl);
        QTextOption appNameOption;
        appNameOption.setAlignment(Qt::AlignLeft | Qt::AlignTop);
        appNameOption.setWrapMode(QTextOption::WordWrap);

        QFont appNamefont(painter.font());
        appNamefont.setPixelSize(12);

        const QFontMetrics fm(appNamefont);

        QString appBody = holdTextInRect(fm, m_bodyText, m_bodyLbl->rect());

        painter.setBrush(Qt::transparent);
        painter.setPen(Qt::black);

        QTextDocument td;
        td.setDefaultTextOption(appNameOption);
        td.setDefaultFont(appNamefont);
        td.setDefaultStyleSheet(DefaultCSS);
        td.setTextWidth(width());
        td.setDocumentMargin(0);
        td.setHtml(HTMLTemplate.arg(appBody));
        td.drawContents(&painter);
    }

    return false;
}

const QString AppBody::holdTextInRect(const QFontMetrics &fm, const QString &text, const QRect &rect) const
{
    const int textFlag = Qt::AlignTop | Qt::AlignLeft | Qt::TextWordWrap;

    if (rect.contains(fm.boundingRect(rect, textFlag, text)))
        return text;

    QString str(text + "...");

    while (true)
    {
        if (str.size() < 4)
            break;

        QRect boundingRect = fm.boundingRect(rect, textFlag, str);
        if (rect.contains(boundingRect))
            break;

        str.remove(str.size() - 4, 1);
    }

    return str;
}
