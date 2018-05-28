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

#ifndef APPBODYLABEL_H
#define APPBODYLABEL_H

#include <QLabel>

class appBodyLabel : public QLabel
{
    Q_OBJECT
public:
    explicit appBodyLabel(QWidget *parent = nullptr);
    void setText(const QString &text);

protected:
    void paintEvent(QPaintEvent *event) Q_DECL_OVERRIDE;

private:
    const QString holdTextInRect(const QFontMetrics &fm, const QString &text, const QRect &rect) const;

private:
    QString m_text;
};

#endif // APPBODYLABEL_H