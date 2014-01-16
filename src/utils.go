package main

import (
	"os/exec"
	"bytes"
	"time"
)

func execAndWait(timeout int, name string, arg ...string) error {
    cmd := exec.Command(name, arg...)
    var stdout, stderr bytes.Buffer
    cmd.Stdout = &stdout
    cmd.Stderr = &stderr
    err := cmd.Start()
    if err != nil {
        logError(err.Error()) // TODO
        return err
    }

    // wait for process finish
    done := make(chan error)
    go func() {
        done <- cmd.Wait()
    }()

    select {
    case <-time.After(time.Duration(timeout) * time.Millisecond):
        if err := cmd.Process.Kill(); err != nil {
            logError(err.Error()) // TODO
            return err
        }
        <-done
        logInfo("time out and process was killed") // TODO
    case err := <-done:
        logInfo("process output: %s", stdout.String())
        if err != nil {
            logError("process error output: %s", stderr.String())
            logError("process done with error = %v", err) // TODO
            return err
        }
    }
    return nil
}
