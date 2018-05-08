/*
 * Copyright (C) 2016 ~ 2018 Deepin Technology Co., Ltd.
 *
 * Author:     kirigaya <kirigaya@mkacg.com>
 *
 * Maintainer: listenerri <listenerri@gmail.com>
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
static const QString TableName_v2 = "notifications2";
static const QString ColumnId = "ID";
static const QString ColumnIcon = "Icon";
static const QString ColumnSummary = "Summary";
static const QString ColumnBody = "Body";
static const QString ColumnAppName = "AppName";
static const QString ColumnCTime = "CTime";
static const QString ColumnReplacesId = "ReplacesId";
static const QString ColumnTimeout = "Timeout";

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

#ifdef QT_DEBUG
        attemptCreateTable();
        return;
#endif

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
#ifdef QT_DEBUG
    m_query.prepare(QString("INSERT INTO %1 (%2, %3, %4, %5, %6, %7, %8)"
                            "VALUES (:icon, :summary, :body, :appname, :ctime, :replacesid, :timeout)") \
                  .arg(TableName_v2, ColumnIcon, ColumnSummary, ColumnBody,
                       ColumnAppName, ColumnCTime, ColumnReplacesId, ColumnTimeout));
    m_query.bindValue(":icon", entity->appIcon());
    m_query.bindValue(":summary", entity->summary());
    m_query.bindValue(":body", entity->body());
    m_query.bindValue(":appname", entity->appName());
    m_query.bindValue(":ctime", entity->ctime());
    m_query.bindValue(":replacesid", entity->replacesId());
    m_query.bindValue(":timeout", entity->timeout());

    if (!m_query.exec()) {
        qWarning() << "insert value to database failed: " << m_query.lastError().text() << entity->id() << entity->ctime();
        return;
    } else {
        qDebug() << "insert value done, time is:" << entity->ctime();
    }

    // to get entity's id in database
    if (!m_query.exec(QString("SELECT last_insert_rowid() FROM %1;").arg(TableName_v2))) {
        qWarning() << "get entity's id failed: " << m_query.lastError().text() << entity->id() << entity->ctime();
        return;
    } else {
        m_query.next();
        entity->setId(m_query.value(0).toString());
        qDebug() << "get entity's id done:" << entity->id();
        emit RecordAdded(entity);
    }
    return;
#endif
///////////////////////////////////////////////////////////////////////
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
#ifdef QT_DEBUG
    m_query.prepare(QString("DELETE FROM %1 WHERE ID = (:id)").arg(TableName_v2));
    m_query.bindValue(":id", id);

    if (!m_query.exec()) {
        qWarning() << "remove value:" << id << "from database failed: " << m_query.lastError().text();
    } else {
        qDebug() << "remove value:" << id;
    }
    return;
#endif
///////////////////////////////////////////////////////////////////////
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
#ifdef QT_DEBUG
    m_query.prepare(QString("DELETE FROM %1").arg(TableName_v2));

    if (!m_query.exec()) {
        qWarning() << "remove all from database failed: " << m_query.lastError().text();
    } else {
        qDebug() << "remove all done";
    }

    // Remove the unused space
    if (!m_query.exec("VACUUM")) {
        qWarning() << "remove the unused space failed: " << m_query.lastError().text();
    } else {
        qDebug() << "remove the unused space done";
    }
    return;
#endif
///////////////////////////////////////////////////////////////////////
    m_query.prepare(QString("DELETE FROM %1").arg(TableName));

    if (!m_query.exec()) {
        qWarning() << "remove all from database failed: " << m_query.lastError().text();
    } else {
#ifdef QT_DEBUG
        qDebug() << "remove all done";
#endif
    }

    // Remove the unused space
    if (!m_query.exec("VACUUM")) {
        qWarning() << "remove the unused space failed: " << m_query.lastError().text();
    } else {
#ifdef QT_DEBUG
        qDebug() << "remove the unused space done";
#endif
    }
}

QString Persistence::getAll()
{
#ifdef QT_DEBUG
    m_query.prepare(QString("SELECT %1, %2, %3, %4, %5, %6 FROM %7")
               .arg(ColumnId, ColumnIcon, ColumnSummary, ColumnBody, ColumnAppName,
                    ColumnCTime, TableName_v2));

    if (!m_query.exec()) {
        qWarning() << "get all from database failed: " << m_query.lastError().text();
    } else {
        qDebug() << "get all done";
    }

    QJsonArray array1;
    while (m_query.next())
    {
        QJsonObject obj
        {
            {"id", m_query.value(0).toString()},
            {"icon", m_query.value(1).toString()},
            {"summary", m_query.value(2).toString()},
            {"body", m_query.value(3).toString()},
            {"name", m_query.value(4).toString()},
            {"time", m_query.value(5).toString()}
        };
        array1.append(obj);
    }
    return QJsonDocument(array1).toJson();
#endif
///////////////////////////////////////////////////////////////////////
    m_query.prepare(QString("SELECT %1, %2, %3, %4, %5, %6 FROM %7")
               .arg(ColumnId, ColumnIcon, ColumnSummary, ColumnBody, ColumnAppName,
                    ColumnCTime, TableName));

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

// TODO:
QString Persistence::getById(const QString &id)
{

}

// TODO:
QString Persistence::get(int offset, int rowCount)
{

}

void Persistence::attemptCreateTable()
{

    m_query.prepare(QString("CREATE TABLE IF NOT EXISTS %1"
                          "("
                          "%2 INTEGER PRIMARY KEY   AUTOINCREMENT,"
                          "%3 TEXT,"
                          "%4 TEXT,"
                          "%5 TEXT,"
                          "%6 TEXT,"
                          "%7 TEXT,"
                          "%8 TEXT,"
                          "%9 TEXT"
                          ");").arg(TableName_v2,
                                ColumnId, ColumnIcon, ColumnSummary,
                                ColumnBody, ColumnAppName, ColumnCTime,
                                ColumnReplacesId, ColumnTimeout));

    if (!m_query.exec()) {
        qWarning() << "create table failed" << m_query.lastError().text();
    }
}
