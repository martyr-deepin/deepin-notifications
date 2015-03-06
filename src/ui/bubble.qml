import QtQuick 2.1
import QtGraphicalEffects 1.0
import Deepin.Widgets 1.0

Item {
    id: bubble
    y: - height
    width: content.width + 20 + 24 * 2
    height: content.height + 20
    layer.enabled: true

    property var notificationObj
    property int textRigthMargin: 10

    signal actionInvoked(int id, string action_id)
    signal dismissed(int id)
    signal expired(int id)
    signal replacedByOther(int id)
    signal aboutToQuit()

    onDismissed: out_timer.stop()
    onReplacedByOther: out_timer.stop()

    function containsMouse() {
        var pos = _bubble.getCursorPos()
        var x = pos.x - _bubble.x
        var y = pos.y - _bubble.y
        return 0 <= x && x <= width && 0 <= y && y <= height
    }

    PropertyAnimation {
        id: in_animation

        target: bubble
        property: "y"
        to: 0
        duration: 300
        easing.type: Easing.OutCubic
    }

    ParallelAnimation {
        id: out_animation

        PropertyAnimation {
            target: bubble
            property: "x"
            to: width
            duration: 500
            easing.type: Easing.OutCubic
        }

        PropertyAnimation {
            target: bubble
            property: "opacity"
            to: 0.2
            duration: 500
            easing.type: Easing.OutCubic
        }

        onStopped: bubble.expired(notificationObj.id)
    }

    Timer {
        id: mouse_in_check_timer
        interval: 500
        repeat: true
        running: true
        onTriggered: {
            if (bubble.containsMouse()) {
                close_button.visible = true
            } else {
                close_button.visible = false
            }
        }
    }

    Timer {
        id: out_timer

        interval: 5000
        onTriggered: {
            if (bubble.containsMouse()) {
                out_timer.restart()
            } else {
                out_animation.start()
            }
        }
    }

    Timer {
        id: about_to_out_timer

        running: out_timer.running
        interval: out_timer.interval - 1000
        onTriggered: bubble.aboutToQuit()
    }

    function _processContentBody(body) {
        var result = body

        result = result.replace("\n", "<br>")

        return result
    }

    function updateContent(content) {
        if (y == -height) {
            in_animation.start()
        } else if (x != 0 || opacity != 1) {
            x = 0
            opacity = 1
            y = -height
            in_animation.start()
        }

        if (notificationObj) {
            bubble.replacedByOther(notificationObj.id)
        }

        out_timer.restart()

        notificationObj = JSON.parse(content)
        icon.icon = notificationObj.image_path || notificationObj.app_icon || "ooxx"
        summary.text = notificationObj.summary
        body.text = _processContentBody(notificationObj.body)

        action_button_area.reset()
        action_image_button.reset()

        var count = 0
        for (var i = 0; i < notificationObj.actions.length; i += 2) {
            if (i + 1 < notificationObj.actions.length
                && notificationObj.actions[i] != "default") {
                if (count == 0) {
                    // there's image action that we support
                    if (action_image_button.supportedTypes.indexOf(notificationObj.actions[i]) != -1) {
                        action_image_button.state = notificationObj.actions[i]
                        break
                    } else {
                        action_button_area.actionOne = notificationObj.actions[i + 1]
                        action_button_area.idOne = notificationObj.actions[i]
                    }
                } else if (count == 1) {
                    action_button_area.actionTwo = notificationObj.actions[i + 1]
                    action_button_area.idTwo = notificationObj.actions[i]
                }
                count++
            }
        }
    }

    RectangularRing {
        id: ring
        visible: false
        outterWidth: innerWidth + 2
        outterHeight: innerHeight + 3
        outterRadius: content.radius + 2
        innerWidth: content.width
        innerHeight: content.height
        innerRadius: content.radius

        verticalCenterOffset: -2

        anchors.centerIn: parent
        anchors.verticalCenterOffset: 2
    }

    GaussianBlur {
        anchors.fill: ring
        source: ring
        radius: 8
        samples: 16
        transparentBorder: true
    }

    Rectangle {
        id: content
        radius: 4
        width: 300
        height: 70
        anchors.centerIn: parent

        gradient: Gradient {
            GradientStop { position: 0.0; color: Qt.rgba(0, 0, 0, 0.75)}
            GradientStop { position: 1.0; color: Qt.rgba(0, 0, 0, 0.85)}
        }

        Rectangle {
            id: bubble_border
            radius: 4
            color: "transparent"
            border.color: Qt.rgba(0, 0, 0, 0.7)
            anchors.fill: parent

            Rectangle {
                id: bubble_inner_border
                radius: 4
                color: "transparent"
                border.color: Qt.rgba(1, 1, 1, 0.1)

                anchors.fill: parent
                anchors.topMargin: 1
                anchors.bottomMargin: 1
                anchors.leftMargin: 1
                anchors.rightMargin: 1
            }

            Item {
                id: bubble_bg
                anchors.fill: bubble_inner_border

                Item {
                    id: icon_place_holder
                    width: 70
                    height: 70

                    DIcon {
                        id: icon
                        width: 48
                        height: 48
                        theme: "Deepin"

                        anchors.centerIn: parent
                    }
                }

                Text {
                    id: summary
                    width: 160
                    elide: Text.ElideRight
                    font.pixelSize: 11
                    textFormat: Text.StyledText
                    color: Qt.rgba(1, 1, 1, 0.5)

                    anchors.left: icon_place_holder.right
                    anchors.top: icon_place_holder.top
                    anchors.topMargin: (icon_place_holder.height - icon.height) / 2
                }

                Flickable {
                    clip: true
                    width: action_button_area.visible ? action_button_area.x - x - bubble.textRigthMargin:
                                                        action_image_button.visible ? action_image_button.x - x - bubble.textRigthMargin:
                                                                                      close_button.x - x - bubble.textRigthMargin
                    height: (summary.text ? 2 : 4) * body.lineHeight
                    contentWidth: width
                    contentHeight: body.implicitHeight

                    anchors.left: summary.left
                    anchors.top: summary.text ? summary.bottom : undefined
                    anchors.verticalCenter: summary.text ? undefined :  parent.verticalCenter

                    Text {
                        id: body
                        width: parent.width
                        height: parent.height
                        color: "white"
                        wrapMode: Text.WrapAnywhere
                        linkColor: "#19A9F9"
                        lineHeight: 14
                        lineHeightMode: Text.FixedHeight
                        textFormat: Text.RichText
                        font.pixelSize: 12

                        onLinkActivated: Qt.openUrlExternally(link)
                    }
                }
            }

            MouseArea {
                hoverEnabled: true
                anchors.fill: bubble_bg

                onClicked: {
                    var default_action_id
                    for (var i = 0; i < notificationObj.actions.length; i += 2) {
                        if (notificationObj.actions[i + 1] == "default") {
                            default_action_id = notificationObj.actions[i]
                        }
                    }
                    if (default_action_id) { bubble.actionInvoked(notificationObj.id, default_action_id) }
                    bubble.dismissed(notificationObj.id)
                }
            }

            ActionButton {
                id: action_button_area

                onAction: {
                    bubble.actionInvoked(notificationObj.id, actionId)
                    bubble.dismissed(notificationObj.id)
                    // force the in_animation to run next time
                    bubble.x += 1
                }

                anchors.right: parent.right
                anchors.verticalCenter: parent.verticalCenter
            }

            ActionImageButton {
                id: action_image_button

                onAction: {
                    bubble.actionInvoked(notificationObj.id, actionId)
                    bubble.dismissed(notificationObj.id)
                    // force the in_animation to run next time
                    bubble.x += 1
                }

                anchors.right: parent.right
                anchors.verticalCenter: parent.verticalCenter
            }

            CloseButton {
                id: close_button
                visible: false
                anchors.top: bubble_bg.top
                anchors.right: bubble_bg.right
                anchors.topMargin: 5
                anchors.rightMargin: 6

                onClicked: bubble.dismissed(notificationObj.id)
            }
        }
    }
}
