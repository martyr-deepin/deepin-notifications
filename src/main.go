package main

import (
	"dlib/dbus"
	"github.com/niemeyer/qml"
)

const (
	_DN_SERVICE = "com.deepin.Notifications"
	_DN_PATH    = "/org/freedesktop/Notifications"
	_DN_IFACE   = "org.freedesktop.Notifications"
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
	return []string{"hello", "world"}
}

func (dn *DeepinNotifications) GetServerInformation() (name, vendor, version, spec_version string) {
	return "DeepinNotifications", "LinuxDeepin", "2.0", "1.2"
}

func (dn *DeepinNotifications) Notify(
	app_name string,
	replaces_id uint32,
	app_icon string,
	summary string,
	body string,
	actions []string,
	hints map[string]dbus.Variant,
	expire_timeout uint32) (id int32) {
	
	showBubble()

	return id
}

func showBubble() {
	execAndWait(3, "python", "notify.py")
}

func main() {
	qml.Init(nil)

	dn := NewDeepinNotifications()
	dbus.InstallOnSession(dn)

	dbus.DealWithUnhandledMessage()

	select {}
}
