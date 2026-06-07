 # Crash Analysis

 This document summarizes the two confirmed native crashes fixed by the current
 compatibility patch set.

 ## Crash 1: first launch after tapping ALLOW

 Observed behavior:

 - The consent dialog appears on first launch
 - Tapping `ALLOW` leads to a black screen and native crash
 - Tapping `don't allow` reaches the main menu normally

 Original crash signature:

 ```text
 CGFontCopyName+44
 CGFontCopyFullName+40
 CTFontCreateWithGraphicsFont+104
 CTFontCreateWithNameAndOptions+64
 CTFontCreateWithName+48
 CTFramesetterSuggestFrameSizeWithConstraints+232
 ```

 Root cause summary:

 - The legacy CoreText stack attempts to create or inspect a fallback font
 - The fallback font path can fail on modern Android systems
 - `CGFontCopyFullName(NULL)` is reached and dereferences a null pointer

 Fix summary:

 - Replace fallback font string `Helvetica` with `Roboto-Regular`
 - Add a null guard in `CTFontCreateWithGraphicsFont` before calling
   `CGFontCopyFullName`

 ## Crash 2: entering a world, then crashing a few seconds later

 Observed behavior:

 - The app gets past the first launch crash
 - A second crash occurs after entering a world

 Crash signature:

 ```text
 CTFontCopyPangoDescription+20
 ```

 Root cause summary:

 - A CoreText font object or its `pango_description` field can be null
 - The legacy code dereferences the pointer without validation

 Fix summary:

 - Patch `CTFontCopyPangoDescription` to return null safely when either the
   `CTFont *` or `CTFont->pango_description` is null

 ## Why only `libCoreText.so` was changed

 The known crashes were both rooted in CoreText call chains. Patching only the
 affected library minimized behavioral risk while preserving the original app
 logic as much as possible.

 ## Current patch state

 The v2 patch includes:

 - v1 fallback font replacement
 - v1 null guard in `CTFontCreateWithGraphicsFont`
 - v2 null guard in `CTFontCopyPangoDescription`
