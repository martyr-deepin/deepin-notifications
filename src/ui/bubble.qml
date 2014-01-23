import QtQuick 2.1
import QtGraphicalEffects 1.0

Item {
    id: bubble
    width: content.width + 20
    height: content.height + 20

    property int leftPadding: 15
    property int rightPadding: 15

    function updateContent(content) {
        var contObj = JSON.parse(content)
        icon.source = contObj.app_icon
        summary.text = contObj.summary
        body.text = contObj.body
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
        height: 80
        anchors.centerIn: parent

        gradient: Gradient {
            GradientStop { position: 0.0; color: Qt.rgba(0, 0, 0, 0.7)}
            GradientStop { position: 1.0; color: Qt.rgba(0, 0, 0, 0.8)}
        }

        Rectangle {
            radius: 10
            color: "transparent"
            border.color: Qt.rgba(1, 1, 1, 0.2)
            anchors.fill: parent

            Image {
                id: icon
                width: 48
                height: 48

                source: "default.png"
                anchors.left: parent.left
                anchors.leftMargin: bubble.leftPadding
                anchors.verticalCenter: parent.verticalCenter

                onStatusChanged: {
                    if(status != Image.Ready && status != Image.Loading) {
                        icon.source = "default.png"
                    }
                }
            }

            Text {
                id: summary

                color: Qt.rgba(1, 1, 1, 0.5)

                anchors.left: icon.right
                anchors.leftMargin: bubble.leftPadding
                anchors.top: icon.top
            }

            Text {
                id: body

                color: "white"
                wrapMode: Text.Wrap
                linkColor: "#19A9F9"
                maximumLineCount: 2

                onLinkActivated: Qt.openUrlExternally(link)

                anchors.left: summary.left
                anchors.right: action.left
                anchors.rightMargin: bubble.rightPadding
                anchors.top: summary.bottom
                anchors.topMargin: 5
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
                    spacing: 6

                    ActionButton{
                        text: "回复"
                    }
                    ActionButton{
                        text: "拒绝"
                    }
                }
            }
        }
    }
}
