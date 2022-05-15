#!/data/data/com.termux/files/usr/bin/bash
termux-open-url "https://wa.me/$(termux-clipboard-get | tr -d '+')"
