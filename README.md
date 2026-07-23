# 🤖 Python → Android Factory
### Jetpack Compose Edition - Build Native Android Apps with Python + Drag & Drop

> Write your app idea in Python or drag widgets on a phone. One Python script generates a **100% native Jetpack Compose (Kotlin + Material 3)** Android Studio project and can auto-compile it to APK.

**No Java boilerplate. No XML layouts. Just Python as the catalyst.**

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Kotlin](https://img.shields.io/badge/Kotlin-1.9.10-7F52FF?style=for-the-badge&logo=kotlin&logoColor=white)](https://kotlinlang.org)
[![Jetpack Compose](https://img.shields.io/badge/Jetpack_Compose-Material3-4285F4?style=for-the-badge&logo=jetpack-compose&logoColor=white)](https://developer.android.com/jetpack/compose)
[![License MIT](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

---

### ✨ What You Got

This zip contains a complete **Android App Factory**:

| File | What it does |
|------|--------------|
| **`visual_editor.html`** | 🎨 Figma-like drag & drop editor - design your app visually |
| **`editor_server.py`** | 🌐 Serves the editor at `http://localhost:5000` + auto-builds APK on Save |
| **`builder.py`** | ⚙️ The Catalyst - Converts JSON/Python spec → Native Compose project + APK |
| **`app_spec.py`** | 📝 Example app definition (edit this!) |
| **`app_spec.json`** | 📦 Exported spec from visual editor |
| **`GeneratedComposeApp/`** | 📱 Sample generated native app (open in Android Studio) |

**Generated apps use:**
- ✅ Jetpack Compose + Material 3 (not old XML)
- ✅ Navigation Compose (multi-screen)
- ✅ Single Activity + Composables
- ✅ Light/Dark theme auto-support
- ✅ Toast, Navigation, TextField state handling built-in

---

### 🚀 Quick Start (30 seconds for your friends)

**Option A: Visual Way (Recommended)**

```bash
# 1. Unzip and enter folder
unzip AndroidFactory_Compose.zip && cd android_app_maker

# 2. Start the drag & drop editor
python editor_server.py
# → Opens http://localhost:5000

# 3. In browser:
#    - Drag Text, Buttons, Inputs onto phone
#    - Click "Save & Auto-Build APK"
#    → Project at ./GeneratedComposeApp/
#    → APK at ./dist/GeneratedComposeApp.apk (if Android SDK installed)
```

**Option B: CLI Way**

```bash
# Edit your app idea
nano app_spec.py

# Generate native Compose project
python builder.py --spec app_spec.py --output ./MyCoolApp

# Auto-build APK (requires JDK + Android SDK)
python builder.py --spec app_spec.py --output ./MyCoolApp --build

# Or open in Android Studio
# Android Studio → Open → MyCoolApp → Run ▶
```

---

### 📖 Detailed How-To

#### 1. Prerequisites

You only need this once:

**For Generating Projects (Required):**
- Python 3.10+ - `python --version`

**For Auto-Building APKs (Optional but nice):**
- JDK 17+ - Download from https://adoptium.net
  ```bash
  java -version
  # Mac: brew install openjdk@17
  # Ubuntu: sudo apt install openjdk-17-jdk
  ```
- Android SDK / Android Studio - https://developer.android.com/studio
  After install, set env var:
  ```bash
  # Mac (add to ~/.zshrc)
  export ANDROID_HOME=$HOME/Library/Android/sdk
  export PATH=$PATH:$ANDROID_HOME/platform-tools
  
  # Linux
  export ANDROID_HOME=$HOME/Android/Sdk
  
  # Windows: Set in System Environment Variables
  ```

**Not needed?** No problem. The generator works without SDK. You just open the generated folder in Android Studio to build.

#### 2. The Visual Drag & Drop Editor

This is the star feature.

- **Left Panel:** Widget palette + App Settings (name, package `com.yourname.app`, primary color)
- **Center:** Phone preview - drop zone. Widgets stack vertically with scroll.
- **Right:** Properties + Live JSON + Widget list
- **Top Bar:** Screen tabs + Add Screen

**Supported Widgets (Compose mapping):**

| Draggable | Compose Code Generated | Props |
|-----------|------------------------|-------|
| Text Label | `Text()` | text |
| Button | `Button(onClick={...})` | text, action: `showToast:Hi`, `navigate:About`, `finish` |
| Text Input | `OutlinedTextField` + `remember{mutableStateOf}` | hint |
| Image | `Image(painterResource)` | - |
| Switch | `Switch` + state | text |
| Spacer | `Spacer(height)` | height |

**Actions:**
- `showToast:Hello Eugene!` → Shows Android Toast
- `navigate:About` → Navigates to About screen via NavController
- `finish` → Goes back / closes activity

**Export:**
- `Save & Auto-Build APK` → If server running, POSTs JSON to Python, generates project, tries `gradlew assembleDebug`
- `Download spec.json` → Downloads spec for CLI use

#### 3. The Spec File Explained

You can design visually OR code it. JSON example:

```json
{
  "app_name": "My First App",
  "package_name": "com.eugene.myfirstapp",
  "primary_color": "#6200EE",
  "screens": [
    {
      "name": "Home",
      "activity_name": "MainActivity",
      "layout_name": "activity_main",
      "widgets": [
        {"type": "TextView", "id": "welcome", "text": "Hello from Python!"},
        {"type": "Button", "id": "btn1", "text": "Go to About", "action": "navigate:About"},
        {"type": "EditText", "id": "nameInput", "hint": "Enter name"}
      ]
    },
    {
      "name": "About",
      "activity_name": "AboutActivity",
      "layout_name": "activity_about",
      "widgets": [
        {"type": "TextView", "id": "about", "text": "Built with Python!"},
        {"type": "Button", "id": "back", "text": "Back", "action": "finish"}
      ]
    }
  ]
}
```

You can also use `app_spec.py` with same dict as `APP_CONFIG`.

**Tips:**
- `name` = Navigation route
- `activity_name` = Becomes `HomeScreen` Composable function
- Widget `id` must be unique per screen
- Add as many screens as you want

#### 4. Building APKs

**Debug APK (for testing):**
```bash
python builder.py --spec app_spec.json --output ./MyApp --build
# Result: dist/MyApp.apk + app/build/outputs/apk/debug/app-debug.apk
```

**Manual Build:**
```bash
cd MyApp
./gradlew assembleDebug
# APK at app/build/outputs/apk/debug/app-debug.apk
```

**Release APK (for Play Store):**
1. Generate keystore once:
   ```bash
   keytool -genkey -v -keystore my-release-key.jks -keyalg RSA -keysize 2048 -validity 10000 -alias my-key
   ```
2. In `MyApp/app/build.gradle` add signing config (Android Studio will guide)
3. Build:
   ```bash
   ./gradlew assembleRelease
   ```

#### 5. Installing on Phone

```bash
# Via ADB
adb install dist/MyApp.apk

# Or copy APK to phone and tap to install (enable Unknown Sources)
```

For emulator: Open Android Studio → Device Manager → Create Virtual Device → Run.

#### 6. How the Catalyst Works (For Nerds)

```
[visual_editor.html] --(JSON)--> [builder.py] --(templates)--> [Jetpack Compose Kotlin Project]
                                   |
                                   +-> Generates:
                                       - AndroidManifest.xml
                                       - build.gradle (Compose BOM, Navigation)
                                       - ui/theme/Color.kt, Theme.kt, Type.kt
                                       - MainActivity.kt with:
                                         * @Composable Screen functions
                                         * NavHost + rememberNavController
                                         * MaterialTheme + Surface
                                         * State handling for TextFields
                                       - gradle wrapper

                                   +-> Optional: ./gradlew assembleDebug → APK
```

**Why Compose and not XML?**
- Modern Google standard (2024+)
- 100% Kotlin
- No `findViewById`, no XML layouts
- Easier to generate from Python
- Better Material 3 theming
- Future-proof

#### 7. Customizing & Extending

**Add a new widget type:**
1. In `visual_editor.html`, add to palette HTML and `widget_to_compose` handling in JS
2. In `builder.py`, add case in `widget_to_compose()` function:
   ```python
   elif t == "MyWidget":
       return f'            MyComposable(...)'
   ```
3. Add import in generated MainActivity imports list

**Change theme:**
Edit `primary_color` in editor, or directly in `Color.kt` generation.

**Add dependencies:**
Edit `BUILD_GRADLE_APP` template in builder.py (e.g., add Retrofit, Room)

---

### 📁 Project Structure After Generation

```
GeneratedComposeApp/
├── app/
│   ├── build.gradle             # Compose deps: BOM, navigation, material3
│   ├── src/main/
│   │   ├── AndroidManifest.xml
│   │   └── java/com/eugene/myfirstapp/
│   │       ├── MainActivity.kt  # All your screens as @Composable
│   │       └── ui/theme/
│   │           ├── Color.kt     # Primary color from Python
│   │           ├── Theme.kt     # Light/Dark MaterialTheme
│   │           └── Type.kt
│   └── proguard-rules.pro
├── build.gradle
├── settings.gradle
├── gradle.properties
└── gradlew
```

### 🎯 Example Apps You Can Build Now

1. **Todo App:** Text Input + Button `showToast:Added!` + multiple TextViews
2. **Quiz App:** Multiple screens, navigate between Q1 → Q2 → Result
3. **Business App:** Home with Image + Text + Button navigate to Contact screen with EditTexts
4. **Prototype:** Drag 10 widgets in 2 minutes to show client

---

### ❓ Troubleshooting

**Q: `Java not found` when --build**
A: Install JDK 17+: `brew install openjdk@17` or from adoptium.net, then `export JAVA_HOME=...`

**Q: `Android SDK not found`**
A: Install Android Studio, or set `ANDROID_HOME`. You can still generate project without it, just open in Android Studio to build.

**Q: `gradle: command not found`**
A: Use Android Studio, or install gradle: `brew install gradle`, or generate wrapper in Android Studio once.

**Q: Generated project won't sync in Android Studio**
A: File → Invalidate Caches / Restart. Ensure Android Studio Giraffe or newer (for Compose BOM).

**Q: Visual editor Save & Build says "No server"**
A: You opened HTML file directly. Run `python editor_server.py` first and use http://localhost:5000. Otherwise it just downloads JSON - run `python builder.py --spec app_spec.json --build` manually.

**Q: How to share with friends?**
A: Send them the `AndroidFactory_Compose.zip`. They unzip, run `python editor_server.py`, design, build. They still need Android Studio for final APK unless they install SDK.

---

### 🔮 Next Steps / Roadmap

- [ ] More widgets: LazyColumn lists, Card, TopAppBar, Bottom Nav, Google Maps Compose
- [ ] State management: ViewModel generation
- [ ] Networking: Auto-generate Retrofit calls from Python spec
- [ ] Icon generator: Python creates launcher icons from color
- [ ] One-click Play Store upload via `builder.py --publish`
- [ ] Cloud build: Build APK on server without local SDK (like EAS Build)

Want any of these? Edit builder.py - it's all Python templates.

---

### 📄 License

MIT - Share freely with friends. If you build a cool app, send me a screenshot!

**Made with Python as catalyst. From Eugene, OR with ❤️**

---

### Quick Reference Card for Friends

```
1. python editor_server.py
2. Drag widgets → Save & Auto-Build
3. If auto-build fails: Open GeneratedComposeApp in Android Studio → Run
4. APK → dist/*.apk → Install on phone
5. To publish: Build → Generate Signed Bundle / APK in Android Studio
```
