/*
 * Copyright (C) 2016 ~ 2018 Deepin Technology Co., Ltd.
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

#include "persistence.h"

#include <QStandardPaths>
#include <QSqlError>
#include <QSqlRecord>
#include <QDebug>
#include <QDir>
#include <QJsonDocument>
#include <QJsonArray>
#include <QJsonObject>

#include "notificationentity.h"

static const QString TableName = "notifications";
static const QString ColumnId = "ID";
static const QString ColumnIcon = "Icon";
static const QString ColumnSummary = "Summary";
static const QString ColumnBody = "Body";
static const QString ColumnAppName = "AppName";
static const QString ColumnCTime = "CTime";

Persistence::Persistence(QObject *parent)
    : QObject(parent)
{
    const QString dataDir = QStandardPaths::writableLocation(QStandardPaths::AppDataLocation);

    QDir dir(dataDir);
    if (!dir.exists()) {
        dir.mkpath(dataDir);
    }

    m_dbConnection = QSqlDatabase::addDatabase("QSQLITE", "QSQLITE");
    m_dbConnection.setDatabaseName(dataDir + "/" + "data.db");
    if (!m_dbConnection.open()) {
        qWarning() << "open database error" << m_dbConnection.lastError().text();
    } else {
#ifdef QT_DEBUG
        qDebug() << "database open";
#endif
    }

    m_query = QSqlQuery(m_dbConnection);
    m_query.setForwardOnly(true);
    m_query.prepare(QString("CREATE TABLE IF NOT EXISTS %1"
                          "("
                          "%2 TEXT,"
                          "%3 TEXT,"
                          "%4 TEXT,"
                          "%5 TEXT,"
                          "%6 TEXT,"
                          "%7 TEXT PRIMARY KEY"
                          ");").arg(TableName, ColumnId, ColumnIcon, ColumnSummary, ColumnBody, ColumnAppName, ColumnCTime));

    if (!m_query.exec()) {
        qWarning() << "create table failed" << m_query.lastError().text();
    }
}

void Persistence::addOne(NotificationEntity *entity)
{
    m_query.prepare(QString("INSERT INTO %1 (%2, %3, %4, %5, %6, %7) VALUES (:id, :icon, :summary, :body, :appname, :ctime)") \
                  .arg(TableName, ColumnId, ColumnIcon, ColumnSummary, ColumnBody, ColumnAppName, ColumnCTime));
    m_query.bindValue(":id", entity->id());
    m_query.bindValue(":icon", entity->appIcon());
    m_query.bindValue(":summary", entity->summary());
    m_query.bindValue(":body", entity->body());
    m_query.bindValue(":appname", entity->appName());
    m_query.bindValue(":ctime", entity->ctime());

    if (!m_query.exec()) {
        qWarning() << "insert value to database failed: " << m_query.lastError().text() << entity->id() << entity->ctime();
    } else {
#ifdef QT_DEBUG
        qDebug() << "insert value " << entity->ctime();
#endif
    }

    emit RecordAdded(entity);
}

void Persistence::addAll(QList<NotificationEntity *> entities)
{
    for (NotificationEntity *entity : entities) {
        addOne(entity);
    }
}

void Persistence::removeOne(const QString &id)
{
    m_query.prepare(QString("DELETE FROM %1 WHERE ctime = (:ctime)").arg(TableName));
    m_query.bindValue(":ctime", id);

    if (!m_query.exec()) {
        qWarning() << "remove value:" << id << "from database failed: " << m_query.lastError().text();
    } else {
#ifdef QT_DEBUG
        qDebug() << "remove value:" << id;
#endif
    }
}

void Persistence::removeAll()
{
    m_query.prepare(QString("DELETE FROM %1").arg(TableName));

    if (!m_query.exec()) {
        qWarning() << "remove all from database failed: " << m_query.lastError().text();
    } else {
#ifdef QT_DEBUG
        qDebug() << "remove all done";
#endif
    }
}

QString Persistence::getAll()
{
    m_query.prepare(QString("SELECT %1, %2, %3, %4, %5, %6 FROM %7")
               .arg(ColumnId, ColumnIcon, ColumnSummary, ColumnBody, ColumnAppName, ColumnCTime, TableName));

    if (!m_query.exec()) {
        qWarning() << "get all from database failed: " << m_query.lastError().text();
    } else {
#ifdef QT_DEBUG
        qDebug() << "get all done";
#endif
    }

    QJsonArray array;
    while (m_query.next())
    {
        QJsonObject obj
        {
            {"name", m_query.value(4).toString()},
            {"icon", m_query.value(1).toString()},
            {"summary", m_query.value(2).toString()},
            {"body", m_query.value(3).toString()},
            {"id", m_query.value(0).toString()},
            {"time", m_query.value(5).toString()}
        };
        array.append(obj);
    }
    return QJsonDocument(array).toJson();
}
