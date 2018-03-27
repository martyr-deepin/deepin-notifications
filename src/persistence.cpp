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
#include <QSqlQuery>
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
        qDebug() << "database open";
    }

    QSqlQuery query(m_dbConnection);
    query.prepare(QString("CREATE TABLE IF NOT EXISTS %1"
                          "("
                          "%2 TEXT,"
                          "%3 TEXT,"
                          "%4 TEXT,"
                          "%5 TEXT,"
                          "%6 TEXT,"
                          "%7 TEXT PRIMARY KEY"
                          ");").arg(TableName, ColumnId, ColumnIcon, ColumnSummary, ColumnBody, ColumnAppName, ColumnCTime));

    if (!query.exec()) {
        qWarning() << "create table failed" << query.lastError().text();
    }
}

void Persistence::addOne(NotificationEntity *entity)
{
    QSqlQuery query(m_dbConnection);
    query.prepare(QString("INSERT INTO %1 (%2, %3, %4, %5, %6, %7) VALUES (:id, :icon, :summary, :body, :appname, :ctime)") \
                  .arg(TableName, ColumnId, ColumnIcon, ColumnSummary, ColumnBody, ColumnAppName, ColumnCTime));
    query.bindValue(":id", entity->id());
    query.bindValue(":icon", entity->appIcon());
    query.bindValue(":summary", entity->summary());
    query.bindValue(":body", entity->body());
    query.bindValue(":appname", entity->appName());
    query.bindValue(":ctime", entity->ctime());

    if (!query.exec()) {
        qWarning() << "insert value to database failed: " << query.lastError().text() << entity->id() << entity->ctime();
    } else {
        qDebug() << "insert value " << entity->ctime();
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
    QSqlQuery query(m_dbConnection);
    query.prepare(QString("DELETE FROM %1 WHERE ctime = (:ctime)").arg(TableName));
    query.bindValue(":ctime", id);
    query.exec();
}

void Persistence::removeAll()
{
    QSqlQuery query(m_dbConnection);
    query.prepare(QString("DELETE FROM %1").arg(TableName));
    query.exec();
}

QString Persistence::getAll()
{
    QSqlQuery query(QString("SELECT * FROM %1").arg(TableName), m_dbConnection);

    const int idName = query.record().indexOf(ColumnId);
    const int iconName = query.record().indexOf(ColumnIcon);
    const int summaryName = query.record().indexOf(ColumnSummary);
    const int bodyName = query.record().indexOf(ColumnBody);
    const int appNameName = query.record().indexOf(ColumnAppName);
    const int ctimeName = query.record().indexOf(ColumnCTime);

    QJsonArray array;

    while (query.next())
    {
        QJsonObject obj
        {
            {"name", query.value(appNameName).toString()},
            {"icon", query.value(iconName).toString()},
            {"summary", query.value(summaryName).toString()},
            {"body", query.value(bodyName).toString()},
            {"id", query.value(idName).toString()},
            {"time", query.value(ctimeName).toString()}
        };
        array.append(obj);
    }

    return QJsonDocument(array).toJson();
}
