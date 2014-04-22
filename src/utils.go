package main

import (
	"dbus/org/freedesktop/dbus"
	"encoding/json"
)

var dbusInterface *dbus.DBusDaemon

func init() {
	var err error
	dbusInterface, err = dbus.NewDBusDaemon("org.freedesktop.DBus", "/org/freedesktop/DBus")
	if err != nil {
		logger.Info(err)
	}
}

type NotificationInfo struct {
	Id      uint32   `json:"id"`
	AppName string   `json:"app_name"`
	AppIcon string   `json:"app_icon"`
	Summary string   `json:"summary"`
	Body    string   `json:"body"`
	Actions []string `json:"actions"`
	// variables below are fetched from hints parameter
	ImagePath string `json:"image_path"`
}

func (ni *NotificationInfo) FromJSON(jsonString string) {
	err := json.Unmarshal([]byte(jsonString), ni)
	if err != nil {
		logger.Info(err)
	}
}

func (ni *NotificationInfo) ToJSON() string {
	result, err := json.Marshal(ni)
	if err != nil {
		logger.Info(err)
	}
	return string(result)
}

func actionsEqual(actionsOne, actionsTwo []string) bool {
	if len(actionsOne) != len(actionsTwo) {
		return false
	}
	for i := 0; i < len(actionsOne); i++ {
		if !(actionsOne[i] == actionsTwo[i]) {
			return false
		}
	}
	return true
}

func (ni *NotificationInfo) Equal(another *NotificationInfo) bool {
	if ni.AppName == another.AppName &&
		ni.AppIcon == another.AppIcon &&
		ni.Summary == another.Summary &&
		ni.Body == another.Body &&
		ni.ImagePath == another.ImagePath &&
		actionsEqual(ni.Actions, another.Actions) {
		return true
	}
	return false
}

func checkServiceExistence(serviceName string) bool {
	result, err := dbusInterface.NameHasOwner(serviceName)
	if err != nil || !result {
		return false
	}
	return true
}
