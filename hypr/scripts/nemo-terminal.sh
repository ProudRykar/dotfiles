#!/bin/bash

ACTIVE=$(hyprctl activewindow -j | jq -r '.class')

if [[ "$ACTIVE" == "Nemo" || "$ACTIVE" == "org.gnome.Nemo" ]]; then
    DIR=$(gdbus call --session \
      --dest org.Nemo \
      --object-path /org/Nemo/window/1 \
      --method org.freedesktop.FileManager1.ShowFolders 2>/dev/null)

    [ -z "$DIR" ] && DIR="$HOME"
else
    DIR="$HOME"
fi

foot --working-directory "$DIR"

