# Third-Party Software Licenses

This document contains the licenses for third-party software used in Storymaster.

## PySide6

**License:** LGPL v3  
**Copyright:** The Qt Company Ltd.  
**Website:** https://www.qt.io/qt-for-python  

This software uses PySide6, which is licensed under the GNU Lesser General Public License (LGPL) version 3. You can find the full text of the LGPL v3 license at: https://www.gnu.org/licenses/lgpl-3.0.html

**LGPL Compliance Notice:**
PySide6 is dynamically linked as a separate library and can be replaced by users. The source code for PySide6 is available from The Qt Company and the Python Package Index (PyPI).

## SQLAlchemy

**License:** MIT License  
**Copyright:** 2006-2023 SQLAlchemy authors and contributors  
**Website:** https://www.sqlalchemy.org/  

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## PyEnchant

**License:** LGPL v2.1  
**Copyright:** Ryan Kelly and contributors  
**Website:** https://github.com/pyenchant/pyenchant  

This software optionally uses PyEnchant for spell checking functionality, which is licensed under the GNU Lesser General Public License (LGPL) version 2.1. The full text is available at: https://www.gnu.org/licenses/lgpl-2.1.html

## Faker

**License:** MIT License  
**Copyright:** 2012-2023 Daniele Faraglia and contributors  
**Website:** https://github.com/joke2k/faker  

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## PyInstaller

**License:** GPL v2 with exception for generated executables  
**Copyright:** PyInstaller Development Team  
**Website:** https://www.pyinstaller.org/  

PyInstaller is used only as a build tool to create executables. The generated executables are not bound by PyInstaller's GPL license due to the runtime exception. Full license details at: https://github.com/pyinstaller/pyinstaller/blob/develop/COPYING.txt

## Development Dependencies

The following dependencies are used only during development and testing:

- **pytest:** MIT License
- **black:** MIT License  
- **isort:** MIT License

---

**Note:** This software complies with all LGPL requirements by dynamically linking LGPL libraries and ensuring users can replace them independently.