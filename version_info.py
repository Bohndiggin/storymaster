# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx

# Get version from package
try:
    import storymaster
    version_parts = storymaster.__version__.split('.')
    # Ensure we have 4 parts for Windows version info
    while len(version_parts) < 4:
        version_parts.append('0')
    version_tuple = tuple(int(x) for x in version_parts[:4])
except:
    # Fallback if import fails
    version_tuple = (1, 0, 0, 0)

VSVersionInfo(
    ffi=FixedFileInfo(
        # filevers and prodvers should be always a tuple with four items: (1, 2, 3, 4)
        # Set not needed items to zero 0.
        filevers=version_tuple,
        prodvers=version_tuple,
        # Contains a bitmask that specifies the valid bits 'flags'r
        mask=0x3F,
        # Contains a bitmask that specifies the Boolean attributes of the file.
        flags=0x0,
        # The operating system for which this file was designed.
        # 0x4 - NT and there is no need to change it.
        OS=0x40004,
        # The general type of file.
        # 0x1 - the file is an application.
        fileType=0x1,
        # The function of the file.
        # 0x0 - the function is not defined for this fileType
        subtype=0x0,
        # Creation date and time stamp.
        date=(0, 0),
    ),
    kids=[
        StringFileInfo(
            [
                StringTable(
                    "040904B0",
                    [
                        StringStruct("CompanyName", "Storymaster Development"),
                        StringStruct(
                            "FileDescription", "Storymaster - Creative Writing Tool"
                        ),
                        StringStruct("FileVersion", getattr(storymaster, '__version__', '1.0.0')),
                        StringStruct("InternalName", "storymaster"),
                        StringStruct("LegalCopyright", "Copyright (C) 2025"),
                        StringStruct("OriginalFilename", "storymaster.exe"),
                        StringStruct("ProductName", "Storymaster"),
                        StringStruct("ProductVersion", getattr(storymaster, '__version__', '1.0.0')),
                    ],
                )
            ]
        ),
        VarFileInfo([VarStruct("Translation", [1033, 1200])]),
    ],
)
