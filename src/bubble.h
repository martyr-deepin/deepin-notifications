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

private:
    NotificationEntity *m_entity;
    void updateContent();
};

#endif // BUBBLE_H
