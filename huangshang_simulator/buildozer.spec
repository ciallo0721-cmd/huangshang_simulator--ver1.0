[app]
title = 皇上模拟器
package.name = huangshangsimulator
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,ttf
version = 1.0
requirements = python3, kivy, pygame, android

android.permissions = INTERNET
android.api = 28
android.minapi = 21
android.ndk = 19b
p4a.branch = master

icon.filename = icons/icon-48.png
orientation = portrait
fullscreen = 1
log_level = 2

android.accept_sdk_license = True
android.arch = armeabi-v7a

source.include_patterns = fonts/*,icons/*