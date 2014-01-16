package main

import (
	"dlib/dbus"
	"os/exec"
)

var _SERVER_CAPS_ = []string{"action-icons", "actions",
	"body", "body-hyperlinks", "body-markup"}
var _SERVER_INFO_ = []string{"DeepinNotifications",
	"LinuxDeepin", "2.0", "1.2"}

const (
	_DN_SERVICE = "com.deepin.Notifications"
	_DN_PATH    = "/org/freedesktop/Notifications"
	_DN_IFACE   = "org.freedesktop.Notifications"

	_SUBPROCESS_TIMEOUT_ = 10000
)

type DeepinNotifications struct {
	NotificationClosed func(id uint32, reason uint32)
	ActionInvoked      func(id uint32, action_key string)
}

func NewDeepinNotifications() *DeepinNotifications {
	dn := &DeepinNotifications{}

	return dn
}

func (dn *DeepinNotifications) GetDBusInfo() dbus.DBusInfo {
	return dbus.DBusInfo{_DN_SERVICE, _DN_PATH, _DN_IFACE}
}

func (dn *DeepinNotifications) CloseNotification(id uint32) {
}

func (dn *DeepinNotifications) GetCapbilities() []string {
	return _SERVER_CAPS_
}

func (dn *DeepinNotifications) GetServerInformation() (name, vendor, version, spec_version string) {
	return _SERVER_INFO_[0], _SERVER_INFO_[1], _SERVER_INFO_[2], _SERVER_INFO_[3]
}

func (dn *DeepinNotifications) Notify(
	app_name string,
	replaces_id uint32, // we don't support the feature
	app_icon string,
	summary string,
	body string,
	actions []string,
	hints map[string]dbus.Variant,
	expire_timeout uint32) (id int32) {

	showBubble(&NotificationInfo{app_name, app_icon, summary, body, actions})

	return id
}

func showBubble(ni *NotificationInfo) {
	cmd := exec.Command("python", "notify.py", ni.ToJSON())
	cmd.Start()
}

func main() {
	dn := NewDeepinNotifications()
	dbus.InstallOnSession(dn)
	dbus.DealWithUnhandledMessage()
	
	logInit()

	select {}
}
