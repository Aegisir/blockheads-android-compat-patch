 # CoreText Call Chain Notes

 This note captures the important reverse engineering conclusions used to build
 the compatibility patch.

 ## First crash chain

 Known stack:

 ```text
 CGFontCopyName
 CGFontCopyFullName
 CTFontCreateWithGraphicsFont
 CTFontCreateWithNameAndOptions
 CTFontCreateWithName
 CTFramesetterSuggestFrameSizeWithConstraints
 ```

 Key conclusion:

 - `CGFontCopyName` dereferences a field from `r0`
 - A null `CGFont *` reaches this code path through legacy fallback font logic
 - The old fallback name `Helvetica` is a practical compatibility hazard on
   modern Android runtime environments used by the game

 ## Second crash chain

 Relevant function:

 ```text
 CTFontCopyPangoDescription
 ```

 Original logic summary:

 - Load `CTFont *`
 - Read field at offset `0x0c`
 - Call into a helper without checking for null

 Patched behavior:

 - Return safely when the input font pointer is null
 - Return safely when the `pango_description` field is null

 ## Design rule used during patching

 Keep the patch as narrow as possible:

 - do not alter high-level game flow
 - do not bypass the consent path
 - do not change unrelated native libraries
 - only guard invalid font state reaching old text-layout code
