/**
 * Copyright (C) 2014 Deepin Technology Co., Ltd.
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3 of the License, or
 * (at your option) any later version.
 **/

import QtQuick 2.2

MouseArea {
    id: action_button
    width: Math.max(70, Math.min(Math.max(actionOneText.implicitWidth, actionTwoText.implicitWidth) + 10, 150))
    height: 70
    hoverEnabled: true
    visible: actionOne

    property alias actionOne: canvas.actionOne
    property alias actionTwo: canvas.actionTwo
    property string idOne
    property string idTwo

    property bool mouseInOne: containsMouse && (actionTwo ? mouseY < height / 2 : true)
    property bool mouseInTwo: containsMouse && mouseY > height / 2

    property int radius: 3

    signal action(string actionId)

    onActionOneChanged: canvas.requestPaint()
    onActionTwoChanged: canvas.requestPaint()

    onPositionChanged: canvas.requestPaint()
    onEntered: canvas.requestPaint()
    onExited: canvas.requestPaint()
    onPressed: canvas.requestPaint()
    onReleased: canvas.requestPaint()
    onClicked: {
        if (mouseInOne) {
            action(idOne)
        } else {
            action(idTwo)
        }
    }

    function reset() {
        actionOne = ""
        actionTwo = ""
        idOne = ""
        idTwo = ""
    }

    Canvas {
        id: canvas
        antialiasing: false
        anchors.fill: parent

        property string actionOne
        property string actionTwo

        onPaint: {
            var ctx = getContext("2d")
            ctx.clearRect(region.x, region.y, region.width, region.height)
            ctx.strokeStyle = Qt.rgba(1, 1, 1, 0.1)

            if (actionTwo) {
                ctx.beginPath()
                ctx.moveTo(0, 0)
                ctx.lineTo(width - action_button.radius, 0)
                ctx.arcTo(width, 0, width, action_button.radius, action_button.radius)
                ctx.lineTo(width, height / 2)
                ctx.lineTo(0, height / 2)
                ctx.closePath()
                if (action_button.mouseInOne) {
                    if (action_button.pressed) {
                        var gradient = ctx.createLinearGradient(5, 1, 5, height / 2)
                        gradient.addColorStop(0.0, Qt.rgba(0, 0, 0, 0.2))
                        gradient.addColorStop(1.0, Qt.rgba(0, 0, 0, 0.3))
                        ctx.fillStyle = gradient
                        actionOneText.color = "#888"
                    } else {
                        var gradient = ctx.createLinearGradient(5, 1, 5, height / 2)
                        gradient.addColorStop(0.0, Qt.rgba(1, 1, 1, 0.1))
                        gradient.addColorStop(1.0, Qt.rgba(1, 1, 1, 0.05))
                        ctx.fillStyle = gradient
                        actionOneText.color = "#fff"
                    }
                } else {
                    ctx.fillStyle = "transparent"
                    actionOneText.color = "#fff"
                }
                ctx.fill()

                ctx.beginPath()
                ctx.moveTo(0, height)
                ctx.lineTo(width - action_button.radius, height)
                ctx.arcTo(width, height, width, action_button.height - action_button.radius,action_button.radius)
                ctx.lineTo(width, height / 2)
                ctx.lineTo(0, height / 2)
                ctx.closePath()
                if (action_button.mouseInTwo) {
                    if (action_button.pressed) {
                        var gradient = ctx.createLinearGradient(5, height / 2, 5, height - 1)
                        gradient.addColorStop(0.0, Qt.rgba(0, 0, 0, 0.2))
                        gradient.addColorStop(1.0, Qt.rgba(0, 0, 0, 0.3))
                        ctx.fillStyle = gradient
                        actionTwoText.color = "#888"
                    } else {
                        var gradient = ctx.createLinearGradient(5, height / 2, 5, height - 1)
                        gradient.addColorStop(0.0, Qt.rgba(1, 1, 1, 0.1))
                        gradient.addColorStop(1.0, Qt.rgba(1, 1, 1, 0.05))
                        ctx.fillStyle = gradient
                        actionTwoText.color = "#fff"
                    }
                } else {
                    ctx.fillStyle = "transparent"
                    actionTwoText.color = "#fff"
                }
                ctx.fill()

                ctx.beginPath()
                ctx.moveTo(1, Math.floor(height / 2))
                ctx.lineTo(width - 2, Math.floor(height / 2))
                ctx.closePath()
                ctx.stroke()
            } else {
                ctx.beginPath()
                ctx.moveTo(0, 0)
                ctx.lineTo(width - action_button.radius, 0)
                ctx.arcTo(width, 0, width, action_button.radius, action_button.radius)
                ctx.lineTo(width, height - action_button.radius)
                ctx.arcTo(width, height, width - action_button.radius, height, action_button.radius)
                ctx.lineTo(0, height)
                ctx.closePath()
                if (action_button.mouseInOne) {
                    if (action_button.pressed) {
                        var gradient = ctx.createLinearGradient(5, 0, 5, height)
                        gradient.addColorStop(0.0, Qt.rgba(0, 0, 0, 0.2))
                        gradient.addColorStop(1.0, Qt.rgba(0, 0, 0, 0.3))
                        ctx.fillStyle = gradient
                        actionOneText.color = "#888"
                    } else {
                        var gradient = ctx.createLinearGradient(5, 0, 5, height)
                        gradient.addColorStop(0.0, Qt.rgba(1, 1, 1, 0.1))
                        gradient.addColorStop(1.0, Qt.rgba(1, 1, 1, 0.05))
                        ctx.fillStyle = gradient
                        actionOneText.color = "#fff"
                    }
                } else {
                    ctx.fillStyle = "transparent"
                    actionOneText.color = "#fff"
                }
                ctx.fill()
            }

            ctx.beginPath()
            ctx.moveTo(0, 2)
            ctx.lineTo(0, height - 2)
            ctx.closePath()
            ctx.stroke()
        }
    }

    Item {
        width: parent.width
        height: parent.actionTwo ? parent.height / 2 : parent.height

        Text {
            id: actionOneText
            width: Math.min(parent.width, implicitWidth)
            height: implicitHeight
            text: action_button.actionOne
            elide: Text.ElideRight
            font.pixelSize: 12
            anchors.centerIn: parent
        }

        anchors.top: parent.top
    }

    Item {
        width: parent.width
        height: parent.actionTwo ? parent.height / 2 : 0

        Text {
            id: actionTwoText
            width: Math.min(parent.width, implicitWidth)
            height: implicitHeight
            text: action_button.actionTwo
            elide: Text.ElideRight
            font.pixelSize: 12
            anchors.centerIn: parent
        }

        anchors.bottom: parent.bottom
    }
}
