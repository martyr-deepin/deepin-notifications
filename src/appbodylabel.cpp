/*
 * Copyright (C) 2017 ~ 2018 Deepin Technology Co., Ltd.
 *
 * Author:     kirigaya <kirigaya@mkacg.com>
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

#include "appbodylabel.h"

#include <QTextDocument>
#include <QEvent>
#include <QPainter>
#include <QDebug>
#include <QApplication>

static const QString DefaultCSS = "body { color: rgba(0,0,0,0.9);}";
static const QString HTMLTemplate = "<body>%1</body>";

appBodyLabel::appBodyLabel(QWidget *parent) : QLabel(parent)
{
    setWordWrap(true);
    setSizePolicy(QSizePolicy::MinimumExpanding, QSizePolicy::Expanding);
}

void appBodyLabel::setText(const QString &text)
{
    m_text = text;

    QTextOption appNameOption;
    appNameOption.setAlignment(Qt::AlignLeft | Qt::AlignTop);
    appNameOption.setWrapMode(QTextOption::WordWrap);

    QFont appNamefont(qApp->font());
    const QFontMetrics fm(appNamefont);

    QLabel::setText(holdTextInRect(fm, m_text, rect()));

    update();
}

const QString appBodyLabel::holdTextInRect(const QFontMetrics &fm, const QString &text, const QRect &rect) const
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
