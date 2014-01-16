package main

import (
	"testing"
)

func TestEqual(t *testing.T) {
	goal := &NotificationInfo{"APP_NAME", "ICON", "SUMMARY", "BODY", []string{"ONE", "TWO"}}	
	ni := &NotificationInfo{"APP_NAME", "ICON", "SUMMARY", "BODY", []string{"ONE", "TWO"}}
	if !goal.Equal(ni) {
		t.Error("")
	}
}

func TestFromJSON(t *testing.T) {
	goal := &NotificationInfo{"APP_NAME", "ICON", "SUMMARY", "BODY", []string{"ONE", "TWO"}}
	ni := &NotificationInfo{}
	ni.FromJSON(`{"app_name":"APP_NAME","app_icon":"ICON","summary":"SUMMARY","body":"BODY","actions":["ONE","TWO"]}`)
	if !goal.Equal(ni) {
		t.Error("")
	}
}

func TestToJSON(t *testing.T) {
	goal := `{"app_name":"APP_NAME","app_icon":"ICON","summary":"SUMMARY","body":"BODY","actions":["ONE","TWO"]}`
	ni := &NotificationInfo{"APP_NAME", "ICON", "SUMMARY", "BODY", []string{"ONE", "TWO"}}
	if (goal != ni.ToJSON()){
		t.Error("")
	}
}
