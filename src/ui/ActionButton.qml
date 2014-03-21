import QtQuick 2.1

Rectangle {
    id: button
    state: "normal"
    
    radius: 3
    color: "transparent"
    width: label.implicitWidth + 10
    height: label.implicitHeight + 6
    border.color: Qt.rgba(1, 1, 1, 0.5)
    
    property alias text: label.text
    
    signal action ()
    
    Text {
        id: label
        color: Qt.rgba(1, 1, 1, 0.5)
        text: ""
        
        anchors.centerIn: parent
    }
    
    states: [
        State{
            name: "normal"
            PropertyChanges {target: label; color: Qt.rgba(1, 1, 1, 0.5)}
            PropertyChanges {target: button; border.color: Qt.rgba(1, 1, 1, 0.5)}
        },
        State{
            name: "hover"
            PropertyChanges {target: label; color: Qt.rgba(1, 0.5, 1, 0.5)}
            PropertyChanges {target: button; border.color: Qt.rgba(1, 0.5, 1, 0.5)}
        },
        State{
            name: "pressed"
            PropertyChanges {target: label; color: Qt.rgba(1, 1, 0.5, 0.5)}
            PropertyChanges {target: button; border.color: Qt.rgba(1, 1, 0.5, 0.5)}
        }
    ]
    
    MouseArea {
        anchors.fill: parent
        hoverEnabled: true
        onPressed: button.state = "pressed"
        onReleased: button.state = "hover"
        onEntered: button.state = "hover"
        onExited: button.state = "normal"
        onClicked: button.action()
    }
}