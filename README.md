# Deepin Notifications

**Description**:  An desktop notifications implementation that constraints to the [Gnome Desktop Notifications Specification](https://developer.gnome.org/notification-spec/).


## Dependencies
This program just needs Qt5 to work properly, but modules like gui, widgets, dbus, qml and qtquick must be provided.

## Installation

Normal build process will work fine:
> mkdir build; cd build
> qmake ..
> make
> make INSTALL_ROOT=/usr install

## Usage

**Basic Usage**
> notify-send hello world

For more details on how to directly interact with this program via DBus, please see [Gnome Desktop Notifications Specification](https://developer.gnome.org/notification-spec/).

## Getting involved

We encourage you to report issues and contribute changes. Please check out the [Contribution Guidelines](http://wiki.deepin.org/index.php?title=Contribution_Guidelines) about how to proceed.

## License

GNU General Public License, Version 3.0
