package main

import (
	"testing"
)

func TestEqual(t *testing.T) {
	goal := &NotificationInfo{110, "APP_NAME", "ICON", "SUMMARY", "BODY", []string{"ONE", "TWO"}}
	ni := &NotificationInfo{110, "APP_NAME", "ICON", "SUMMARY", "BODY", []string{"ONE", "TWO"}}
	if !goal.Equal(ni) {
		t.Error("")
	}
}

func TestFromJSON(t *testing.T) {
	goal := &NotificationInfo{110, "APP_NAME", "ICON", "SUMMARY", "BODY", []string{"ONE", "TWO"}}
	ni := &NotificationInfo{}
	ni.FromJSON(`{"id":110,"app_name":"APP_NAME","app_icon":"ICON","summary":"SUMMARY","body":"BODY","actions":["ONE","TWO"]}`)
	if !goal.Equal(ni) {
		t.Error("")
	}
}

func TestToJSON(t *testing.T) {
	goal := `{"id":110,"app_name":"APP_NAME","app_icon":"ICON","summary":"SUMMARY","body":"BODY","actions":["ONE","TWO"]}`
	ni := &NotificationInfo{110, "APP_NAME", "ICON", "SUMMARY", "BODY", []string{"ONE", "TWO"}}
	if goal != ni.ToJSON() {
		t.Error("")
	}
}
