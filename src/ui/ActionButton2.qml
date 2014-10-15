import QtQuick 2.2

MouseArea {
	id: action_button
	width: 100
	height: 100

	property bool separated: true

	Canvas {
		anchors.fill: parent

		property color normalStyle: "transparent"
		property color hoverStyle:

		onPaint: {
			var ctx = getContext("2d")
			ctx.beginPath()

			ctx

			ctx.closePath()
		}
	}
}