#!/data/data/com.termux/files/usr/bin/bash
result=($(termux-call-log | grep -Po "(?<=\+)[0-9]+(?=\")"))
termux-open-url "https://wa.me/${result[-1]}"
