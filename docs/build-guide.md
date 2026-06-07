 # Build Guide

 This repository documents a compatibility patch for The Blockheads 1.7.6 on
 modern Android releases. You must provide your own legally obtained copy of
 the original APK.

 ## Requirements

 - Python 3.10 or newer
 - Java JDK with `jarsigner`
 - ADB for device installation and crash capture
 - An original APK matching the expected SHA256

 Expected input APK SHA256:

 ```text
 29bd526000c04f24ba10b16da9c6c9a57181e40d9bef48c29526aed29c3371eb
 ```

 ## Patch scope

 The current patch only changes:

 - `lib/armeabi-v7a/libCoreText.so`

 It applies two compatibility fixes:

 1. Replace the legacy fallback font name `Helvetica` with `Roboto-Regular`
 2. Add null guards in CoreText paths that can receive invalid font objects on
    modern Android devices

 ## Local patch flow

 1. Place the original APK somewhere outside this repository.
 2. Run the patch script and provide the APK path and output path.
 3. Re-sign the generated APK with your own key.
 4. Install the signed APK on a test device.

 Example:

 ```bash
 python scripts/patch_blockheads_176.py \
   --input /path/to/the-blockheads-1-7-6.apk \
   --output /path/to/the-blockheads-1-7-6-compat-v2-unsigned.apk
 ```

 ## Signing example

 Example debug signing flow:

 ```bash
 keytool -genkeypair -v -keystore compat-debug.keystore -alias compat-debug \
   -keyalg RSA -keysize 2048 -validity 10000

 jarsigner -verbose -sigalg SHA256withRSA -digestalg SHA-256 \
   -keystore compat-debug.keystore \
   /path/to/the-blockheads-1-7-6-compat-v2-unsigned.apk compat-debug
 ```

 ## Install example

 ```bash
 adb install -r /path/to/the-blockheads-1-7-6-compat-v2-unsigned.apk
 ```

## Validation notes

Recommended checks after install:

- First launch after tapping `ALLOW` no longer crashes immediately
- Entering a world no longer crashes in the first few seconds from the known
  `CTFontCopyPangoDescription` path
- New regressions should be captured with `adb logcat` and DropBox native crash
  records before further patching

Note: the rebuilt APK SHA256 can differ from the repository reference if ZIP
metadata or packaging details differ. The more important consistency check is
that the patched `libCoreText.so` SHA256 matches the expected patched value.
