#!/usr/bin/env python3
"""
Create a proper Windows version info file for PyInstaller
This generates the version_info.py file with proper imports
"""

def create_version_info():
    """Create version_info.py file with simpler format that PyInstaller can handle"""
    # Use the old-style format that PyInstaller expects
    version_content = '''# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx
VSVersionInfo(
  ffi=FixedFileInfo(
# filevers and prodvers should be always a tuple with four items: (1, 2, 3, 4)
# Set not needed items to zero 0.
filevers=(1,0,0,0),
prodvers=(1,0,0,0),
# Contains a bitmask that specifies the valid bits 'flags'r
mask=0x3f,
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
date=(0, 0)
),
kids=[
StringFileInfo(
  [
  StringTable(
    u'040904B0',
    [StringStruct(u'CompanyName', u'Storymaster Development'),
    StringStruct(u'FileDescription', u'Storymaster - Creative Writing Tool'),
    StringStruct(u'FileVersion', u'1.0.0.0'),
    StringStruct(u'InternalName', u'storymaster'),
    StringStruct(u'LegalCopyright', u'Copyright (C) 2025'),
    StringStruct(u'OriginalFilename', u'storymaster.exe'),
    StringStruct(u'ProductName', u'Storymaster'),
    StringStruct(u'ProductVersion', u'1.0.0.0')])
  ]), 
VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
'''
    
    with open('version_info.py', 'w', encoding='utf-8') as f:
        f.write(version_content)
    
    print("Created version_info.py with PyInstaller-compatible format")
    return True

if __name__ == "__main__":
    create_version_info()