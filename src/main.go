package main

import (
	"dbus/com/deepin/bubble"
	"dlib/dbus"
	"os"
	"os/exec"
)

var _SERVER_COUNTER_ = uint32(0)
var _SERVER_CAPS_ = []string{"action-icons", "actions",
	"body", "body-hyperlinks", "body-markup"}
var _SERVER_INFO_ = []string{"DeepinNotifications",
	"LinuxDeepin", "2.0", "1.2"}

const (
	_DN_SERVICE = "org.freedesktop.Notifications"
	_DN_PATH    = "/org/freedesktop/Notifications"
	_DN_IFACE   = "org.freedesktop.Notifications"

	_BUBBLE_SERVICE_ = "com.deepin.Bubble"

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
	expire_timeout int32) uint32 {

	_SERVER_COUNTER_++
	hints_image_path := ""
	if v, ok := hints["image-path"]; ok {
		hints_image_path = v.Value().(string)
	} 
	showBubble(&NotificationInfo{_SERVER_COUNTER_, app_name, app_icon, summary, body, actions, hints_image_path})

	return _SERVER_COUNTER_
}

func fork(ni *NotificationInfo) {
	// _, filename, _, _ := runtime.Caller(1)
	// filename := os.Args[0]
	// logger.Println(filename)
	// cmd := exec.Command("python", path.Join(path.Dir(filename), "notify.py"), ni.ToJSON())
	cmd := exec.Command("python", "/usr/share/deepin-notifications/notify.py", ni.ToJSON())
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	cmd.Start()
}

func showBubble(ni *NotificationInfo) {
	if checkServiceExistence(_BUBBLE_SERVICE_) {
		bb, err := bubble.NewBubble(_BUBBLE_SERVICE_, "/com/deepin/Bubble")
		if err != nil {
			logger.Println(err)
			fork(ni)
		} else {
			bb.UpdateContent(ni.ToJSON())
		}
	} else {
		fork(ni)
	}
}

func main() {
	dn := NewDeepinNotifications()
	dbus.InstallOnSession(dn)
	dbus.DealWithUnhandledMessage()

	if err := dbus.Wait(); err != nil {
		logger.Fatal("lost dbus session:", err)
	}
}
