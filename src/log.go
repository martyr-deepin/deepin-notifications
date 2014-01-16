package main

import (
	"log"
	"os"
)

var logger *log.Logger

func logInit() {
	logger = log.New(os.Stdout, "Deepin Notification", log.Ldate | log.Ltime | log.Llongfile)
}
