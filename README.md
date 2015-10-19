# Deepin Notifications

**Description**:  An implementation of [Gnome Desktop Notifications Specification](https://developer.gnome.org/notification-spec/)


## Dependencies

### Build Dependencies

- Qt5.3 or above.
- Qt modules
    - gui
    - widgets
    - dbus
    - qml
    - quick

### Runtime Dependencies

- DBus

## Installation

Normal build process will work fine:
```
mkdir build; cd build
qmake ..
make
make INSTALL_ROOT=/usr install
```

## Usage

**Basic Usage**
```
notify-send hello world
```

For more detailed information on how to communicate with this program via DBus, please see [Gnome Desktop Notifications Specification](https://developer.gnome.org/notification-spec/).

## Getting help

Any usage issues can ask for help via

* [Gitter](https://gitter.im/orgs/linuxdeepin/rooms)
* [IRC channel](https://webchat.freenode.net/?channels=deepin)
* [Forum](https://bbs.deepin.org)
* [WiKi](http://wiki.deepin.org/)

## Getting involved

We encourage you to report issues and contribute changes
[Contirubtion guide for users](http://wiki.deepin.org/index.php?title=Contribution_Guidelines_for_Users)
[Contribution guide for developers](http://wiki.deepin.org/index.php?title=Contribution_Guidelines_for_Developers).

## License

Deepin Notifications is licensed under [GPLv3](LICENSE).
