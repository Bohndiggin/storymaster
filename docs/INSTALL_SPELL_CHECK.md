# Spell Check Installation Guide

Storymaster uses PyEnchant for spell checking functionality. This requires both the Python package and system-level enchant libraries.

## Linux

### Ubuntu/Debian
```bash
# Install system enchant libraries
sudo apt-get update
sudo apt-get install libenchant-2-2 libenchant-2-dev

# Install dictionaries (optional but recommended)
sudo apt-get install hunspell-en-us hunspell-en-gb aspell-en

# Install Python package (already in requirements.txt)
pip install pyenchant==3.2.2
```

### Fedora/RHEL/CentOS
```bash
# Install system enchant libraries
sudo dnf install enchant2-devel enchant2

# Install dictionaries
sudo dnf install hunspell-en-US hunspell-en-GB aspell-en

# Install Python package
pip install pyenchant==3.2.2
```

### Arch Linux
```bash
# Install system enchant libraries
sudo pacman -S enchant

# Install dictionaries
sudo pacman -S hunspell-en_us hunspell-en_gb aspell-en

# Install Python package
pip install pyenchant==3.2.2
```

## macOS

### Using Homebrew (Recommended)
```bash
# Install enchant via Homebrew
brew install enchant

# Install Python package
pip install pyenchant==3.2.2
```

### Using MacPorts
```bash
# Install enchant via MacPorts
sudo port install enchant2

# Install Python package
pip install pyenchant==3.2.2
```

## Windows

### Method 1: Using pip (Easiest)
```cmd
# PyEnchant includes pre-compiled binaries for Windows
pip install pyenchant==3.2.2
```

### Method 2: Manual Installation
1. Download enchant from: https://github.com/AbiWord/enchant/releases
2. Extract to a directory (e.g., `C:\enchant`)
3. Add the `bin` directory to your PATH environment variable
4. Install the Python package:
   ```cmd
   pip install pyenchant==3.2.2
   ```

## Testing Installation

To verify spell check is working correctly, run this Python test:

```python
import enchant

# Test basic functionality
d = enchant.Dict("en_US")
print(f"'hello' is spelled correctly: {d.check('hello')}")
print(f"'helo' is spelled correctly: {d.check('helo')}")

if not d.check('helo'):
    suggestions = d.suggest('helo')
    print(f"Suggestions for 'helo': {suggestions}")

print("Spell check installation successful!")
```

## Troubleshooting

### Common Issues

**Linux: "enchant library not found"**
- Ensure both `libenchant-2-2` and `libenchant-2-dev` are installed
- Try reinstalling: `pip uninstall pyenchant && pip install pyenchant==3.2.2`

**macOS: "No backend dictionaries available"**
- Install additional dictionaries: `brew install hunspell`
- Check available backends: `python -c "import enchant; print(enchant.list_dicts())"`

**Windows: "DLL load failed"**
- Use the pip installation method (includes pre-compiled binaries)
- Ensure you're using a compatible Python version (3.8+)

**General: "No module named 'enchant'"**
- Activate your virtual environment first
- Reinstall: `pip install pyenchant==3.2.2`

### Fallback Options

If PyEnchant cannot be installed, Storymaster includes fallback spell checking:
- Built-in word list checking
- Aspell integration (if available)
- Hunspell integration (if available)

The spell check system will automatically detect and use the best available backend.

## Language Support

To add support for additional languages:

```bash
# Linux (Ubuntu/Debian)
sudo apt-get install hunspell-de hunspell-fr hunspell-es

# macOS
brew install hunspell

# Windows - dictionaries are included with PyEnchant
```

Check available languages:
```python
import enchant
print("Available dictionaries:", enchant.list_dicts())
```