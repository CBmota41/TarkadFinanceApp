# (c) 2025 Buildozer spec para TarkadFinance
[app]

# Nome do app e domínio
title = TarkadFinance
package.name = tarkadfinance
package.domain = org.mota

# Diretório do código fonte
source.dir = .
source.include_exts = py,png,jpg,kv,atlas

# Versão do app
version = 1.0
orientation = portrait

# Dependências do Python
requirements = python3,kivy==2.1.0,kivymd==1.1.1,matplotlib==3.5.3,pandas==1.5.3,reportlab==4.0.4,pillow==9.5.0,pyjnius,android

# API Android
android.api = 30
android.minapi = 21
android.ndk_api = 21
android.archs = arm64-v8a,armeabi-v7a
p4a.bootstrap = sdl2

# Copiar bibliotecas externas
android.copy_libs = True

# Ícone e splash
icon.filename = %(source.dir)s/icon.png
presplash.filename = %(source.dir)s/presplash.png

# Permissões (mais comuns e seguras)
android.permissions = INTERNET,ACCESS_NETWORK_STATE,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,ACCESS_FINE_LOCATION,CAMERA

# Ativar multitouch
fullscreen = 0

# Logs detalhados
log_level = 2
android.logcat_filters = *:S python:D
android.logcat = True

# Debug
android.debug = 1

# Arquivos e pastas extras a incluir
source.include_patterns = assets/*,images/*

# Caminhos fixos do NDK e SDK (ajustados para seu PC)
android.ndk_path = /home/mota/Desktop/android/android-ndk-r25b
android.sdk_path = /home/mota/Desktop/Androidsdk/cmdline-tools/cmdline-tools


[buildozer]

# Evitar alerta de rodar como root
warn_on_root = 1

# Diretório do Build
build_dir = ./.buildozer
