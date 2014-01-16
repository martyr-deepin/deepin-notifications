package main

import (
	"encoding/json"
)

type NotificationInfo struct {
	AppName string   `json:"app_name"`
	AppIcon string   `json:"app_icon"`
	Summary string   `json:"summary"`
	Body    string   `json:"body"`
	Actions []string `json:"actions"`
}

func (ni *NotificationInfo) FromJSON(jsonString string) {
	err := json.Unmarshal([]byte(jsonString), ni)
	if err != nil {
		logger.Println(err)
	}
}

func (ni *NotificationInfo) ToJSON() string {
	result, err := json.Marshal(ni)
	if err != nil {
		logger.Println(err)
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

func (ni *NotificationInfo) Equal(another *NotificationInfo) bool{
	if (ni.AppName == another.AppName &&
		ni.AppIcon == another.AppIcon &&
		ni.Summary == another.Summary &&
		ni.Body == another.Body &&
		actionsEqual(ni.Actions, another.Actions)) {
		return true
	}
	return false
}
