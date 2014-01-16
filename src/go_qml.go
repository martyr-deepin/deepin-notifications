package main

import (
	"github.com/niemeyer/qml"
)

func main() {
    qml.Init(nil)
    engine := qml.NewEngine()

    component, err := engine.LoadFile("ui/bubble.qml")
    if err != nil {
        panic(err)
    }

    window := component.CreateWindow(nil)
	window.Set("flags", 0x00000800)

    window.Show()
    window.Wait()
}
