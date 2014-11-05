import QtQuick 2.2
import Deepin.Widgets 1.0

Item {
    width: 70
    height: 70
    visible: state

    signal action(string actionId)

    property var supportedTypes: ["deepin-action-locate",
        "deepin-action-next", "deepin-action-upgrade"]

    states: [
        State {
            name: "deepin-action-locate"
            PropertyChanges {
                target: ico
                normal_image: "qrc:///ui/locate_normal.png"
                hover_image: "qrc:///ui/locate_hover.png"
                press_image: "qrc:///ui/locate_press.png"
            }
        },
        State {
            name: "deepin-action-next"
            PropertyChanges {
                target: ico
                normal_image: "qrc:///ui/next_normal.png"
                hover_image: "qrc:///ui/next_hover.png"
                press_image: "qrc:///ui/next_press.png"
            }
        },
        State {
            name: "deepin-action-upgrade"
            PropertyChanges {
                target: ico
                normal_image: "qrc:///ui/upgrade_normal.png"
                hover_image: "qrc:///ui/upgrade_hover.png"
                press_image: "qrc:///ui/upgrade_press.png"
            }
        }
    ]

    function reset() {
        state = ""
    }

    Rectangle {
        width: 1
        height: parent.height - 4
        color: Qt.rgba(1, 1, 1, 0.1)

        anchors.left: parent.left
        anchors.verticalCenter: parent.verticalCenter
    }

    DImageButton {
        id: ico
        anchors.centerIn: parent

        onClicked: parent.action(parent.state)
    }
}
