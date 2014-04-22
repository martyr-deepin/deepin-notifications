package main

import (
	log "dlib/logger"
)

var logger *log.Logger

func init() {
	logger = log.NewLogger("com.deepin.notifications")
}
