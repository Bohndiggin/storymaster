# Windows Security Note

## ⚠️ False Positive Warning

Windows Defender may flag Storymaster as a potential threat. **This is a false positive** common with PyInstaller executables.

### Why This Happens:
- PyInstaller bundles Python code into an executable
- Windows doesn't recognize the signature
- The self-extracting nature triggers heuristic detection

### Solutions:

#### **Option 1: Add Exclusion (Recommended)**
1. Open **Windows Security** → **Virus & threat protection**
2. Click **Manage settings** under "Virus & threat protection settings" 
3. Click **Add or remove exclusions**
4. **Add exclusion** → **File** → Select `storymaster.exe`

#### **Option 2: Override the Block**
1. When Windows blocks the download: Click **"More info"**
2. Click **"Run anyway"**

#### **Option 3: Run from Source** 
```bash
# Install Python 3.11+, then:
git clone [repository]
cd storymaster
python install.py
python storymaster/main.py
```

### ✅ Verification
- **Source code** is fully open and available for inspection
- **No network connections** - Storymaster works offline
- **No system modifications** - just reads/writes your project files
- **Portable** - can run from any folder

### 🔒 Security Commitment
Storymaster is:
- ✅ **Open source** - all code visible
- ✅ **Offline only** - no data transmission  
- ✅ **Sandboxed** - doesn't modify system files
- ✅ **Portable** - doesn't require installation

---

**This is a common issue with Python applications and is purely a false positive detection.**