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