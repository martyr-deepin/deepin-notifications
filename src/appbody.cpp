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

#include "appbody.h"
#include <QPainter>
#include <QVBoxLayout>

AppBody::AppBody(QWidget *parent)
    : QWidget(parent)
{
    setSizePolicy(QSizePolicy::Expanding, QSizePolicy::Fixed);

    m_titleLbl = new appBodyLabel;
    m_bodyLbl = new appBodyLabel;

    m_titleLbl->setStyleSheet("font-weight: 460; color: #303030;");
    m_bodyLbl->setStyleSheet("color: rgba(0,0,0,0.9);");

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
    m_titleLbl->setVisible(!title.isEmpty());

    m_titleLbl->setText(title);
}

void AppBody::setText(const QString &text)
{
    m_bodyLbl->setVisible(!text.isEmpty());

    m_bodyLbl->setText(text);
}
