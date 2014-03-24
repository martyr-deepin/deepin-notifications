import QtQuick 2.1

Rectangle {
    id: button
    state: "normal"
    
    radius: 3
    color: "transparent"
    width: label.width + 10
    height: label.height + 6
    border.color: Qt.rgba(1, 1, 1, 0.5)
    
    property alias text: label.text
    
    signal entered ()
    signal exited ()
    signal action ()
    
    Text {
        id: label
        width: Math.min(48, implicitWidth)
        height: implicitHeight
        elide: Text.ElideRight
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
            PropertyChanges {target: label; color: Qt.rgba(1, 1, 1, 1)}
            PropertyChanges {target: button; border.color: Qt.rgba(1, 1, 1, 1)}
        },
        State{
            name: "pressed"
            PropertyChanges {target: label; color: Qt.rgba(1, 1, 1, 0.3)}
            PropertyChanges {target: button; border.color: Qt.rgba(1, 1, 1, 0.3)}
        }
    ]
    
    MouseArea {
        anchors.fill: parent
        hoverEnabled: true
        onPressed: button.state = "pressed"
        onReleased: button.state = "hover"
        onEntered: {button.state = "hover"; button.entered()}
        onExited: {button.state = "normal"; button.exited()}
        onClicked: button.action()
    }
}