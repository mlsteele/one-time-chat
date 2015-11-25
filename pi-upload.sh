#!/usr/bin/env bash

rsync --exclude "*.store" --exclude "*.pyc" --archive --itemize-changes --compress --partial --progress ./ pi@10.0.0.2:one-time-chat/
