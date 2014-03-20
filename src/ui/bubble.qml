import QtQuick 2.1
import QtGraphicalEffects 1.0

Item {
    id: bubble
    y: - height
    width: content.width + 20
    height: content.height + 20

    property url defaultIcon: "default.png"
    property int leftPadding: (content.height - 48) / 2
    property int rightPadding: (content.height - 48) / 2 
    property var notificationObj

    PropertyAnimation {
        id: in_animation

        running: true
        target: bubble
        property: "y"
        to: 0
        duration: 300
        easing.type: Easing.OutCubic

        onStopped: out_timer.restart()
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

        onStopped: _notify.exit()
    }

    Timer {
        id: out_timer

        interval: 5000
        onTriggered: {
            out_animation.start()
        }
    }

    function updateContent(content) {
        out_timer.restart()
        
        print(content)

        notificationObj = JSON.parse(content)
        icon.source = notificationObj.app_icon
        summary.text = notificationObj.summary
        body.text = notificationObj.body
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
        radius: 10
        samples: 16
        transparentBorder: true
    }

    Rectangle {
        id: content
        radius: 10
        width: 300
        height: 70
        anchors.centerIn: parent

        gradient: Gradient {
            GradientStop { position: 0.0; color: Qt.rgba(0, 0, 0, 0.8)}
            GradientStop { position: 1.0; color: Qt.rgba(0, 0, 0, 0.95)}
        }

        Rectangle {
            radius: 10
            color: "transparent"
            border.color: Qt.rgba(0, 0, 0, 0.7)
            anchors.fill: parent

            Rectangle {
                radius: 10
                color: "transparent"
                border.color: Qt.rgba(1, 1, 1, 0.1)
                anchors.fill: parent
                anchors.topMargin: 1
                anchors.bottomMargin: 1
                anchors.leftMargin: 1
                anchors.rightMargin: 1


                MouseArea {
                    hoverEnabled: true
                    anchors.fill: parent

                    onEntered: {
                        out_timer.stop()
                    }

                    onExited: {
                        out_timer.restart()
                    }
                }

                Image {
                    id: icon
                    width: 48
                    height: 48

                    source: bubble.defaultIcon
                    anchors.left: parent.left
                    anchors.leftMargin: bubble.leftPadding
                    anchors.verticalCenter: parent.verticalCenter
                    
                    property bool checkedFlag: false

                    onStatusChanged: {
                        if(status != Image.Ready && status != Image.Loading) {
                            if (checkedFlag) {
                                icon.source = bubble.defaultIcon
                            } else {
                                icon.source = notificationObj.image_path
                                checkedFlag = true
                            }
                        }
                    }

                    MouseArea {
                        anchors.fill: parent

                        onClicked: {
                            _notify.openSenderProgram()
                        }
                    }
                }

                Text {
                    id: summary
                    width: 200
                    elide: Text.ElideRight
                    font.pixelSize: 11                    
                    color: Qt.rgba(1, 1, 1, 0.5)

                    anchors.left: icon.right
                    anchors.leftMargin: bubble.leftPadding
                    anchors.top: icon.top
                }

                Text {
                    id: body

                    color: "white"
                    wrapMode: Text.WrapAnywhere
                    linkColor: "#19A9F9"
                    font.pixelSize: 11
                    maximumLineCount: 2

                    onLinkActivated: Qt.openUrlExternally(link)

                    anchors.left: summary.left
                    anchors.right: parent.right
                    anchors.rightMargin: bubble.rightPadding
                    anchors.top: summary.bottom
                    anchors.topMargin: 3
                }


                Item {
                    id: action
                    width: action_buttons.width
                    height: action_buttons.height
                    anchors.right: parent.right
                    anchors.rightMargin: bubble.rightPadding
                    anchors.verticalCenter: parent.verticalCenter

                    Column {
                        id: action_buttons

                        visible: false
                        spacing: 6

                        ActionButton{
                            text: "回复"
                        }
                    }
                }
            }
        }
    }
}
