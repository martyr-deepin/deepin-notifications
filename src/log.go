package main

import (
	log "pkg.linuxdeepin.com/lib/log"
)

var logger *log.Logger

func init() {
	logger = log.NewLogger("com.deepin.notifications")
}
