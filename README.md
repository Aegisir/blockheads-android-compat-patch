 # blockheads-android-compat-patch

 Compatibility patch project for running The Blockheads 1.7.6 on modern Android versions.

 This repository contains documentation, patch metadata, sample crash logs, and a local patching script.
 It does not contain the original game APK, extracted game assets, or any signing keys.

 ## Scope

 This project targets the Android release of The Blockheads 1.7.6 and focuses on compatibility fixes for Android 13, Android 14, and Android 15 on modern devices.

 Current fixes cover two native crashes in the legacy Apportable CoreText/CoreGraphics stack:

 1. First-launch consent path crash after tapping ALLOW
 2. In-world crash a few seconds after entering gameplay

 ## Supported input

 The patcher is intended for the original APK with this SHA256:

 ```text
 29bd526000c04f24ba10b16da9c6c9a57181e40d9bef48c29526aed29c3371eb
 ```

 The original `lib/armeabi-v7a/libCoreText.so` SHA256 is:

 ```text
 7701c409a115886e0fed1cab508995796b144136cfb3d5dafd37ffe002e0e412
 ```

 ## What the patch does

 The current patch series only modifies `lib/armeabi-v7a/libCoreText.so`.

 ### v1

 - Changes the CoreText fallback font from `Helvetica` to `Roboto-Regular`
 - Prevents `CTFontCreateWithGraphicsFont` from calling `CGFontCopyFullName(NULL)`

 ### v2

 - Adds a null guard to `CTFontCopyPangoDescription`
 - Prevents dereferencing `CTFont*` or `CTFont->pango_description` when they are null

 ## Repository contents

 - `docs/` implementation and build notes
 - `patches/` machine-readable patch metadata
 - `scripts/` local patching script
 - `samples/` redacted crash examples
 - `analysis/` reverse engineering notes

 ## Usage

 1. Obtain your own legal copy of the original APK.
 2. Run the patch script on the APK.
 3. Re-sign the generated APK with your own test key.
 4. Install it on a device for testing.

 See [docs/build-guide.md](docs/build-guide.md) for the full process.

 ## Legal

 This is an unofficial compatibility patch project.

 - It is not affiliated with the original developer or publisher.
 - It does not distribute the original game.
 - Users must provide their own legally obtained copy of the APK.

 See [DISCLAIMER.md](DISCLAIMER.md) for details.
