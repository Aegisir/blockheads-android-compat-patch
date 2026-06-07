 # Patch Notes

 This repository currently documents one patch line for The Blockheads 1.7.6.

 ## v1

 Changes:

 - Replaced the fallback font reference `Helvetica` with `Roboto-Regular`
 - Added a null guard in `CTFontCreateWithGraphicsFont`

 Result:

 - Fixed the known first-launch `ALLOW` crash path rooted at `CGFontCopyName`

 ## v2

 Changes:

 - Added a null guard in `CTFontCopyPangoDescription`

 Result:

 - Fixed the next confirmed crash path encountered after entering gameplay

 ## Checksums

 Original APK SHA256:

 ```text
 29bd526000c04f24ba10b16da9c6c9a57181e40d9bef48c29526aed29c3371eb
 ```

 Patched v2 APK SHA256:

 ```text
 229e5dec00c64de760546bc734ede7a1fa92ec23d1df5ec3d540f9a94ac06219
 ```

 Original `libCoreText.so` SHA256:

 ```text
 7701c409a115886e0fed1cab508995796b144136cfb3d5dafd37ffe002e0e412
 ```

 Patched v2 `libCoreText.so` SHA256:

 ```text
 892a85c6a4930ad93215017bcf71f3781a7891a56bf320e2000014bd21413d2a
 ```
