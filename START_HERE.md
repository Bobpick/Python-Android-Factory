# START HERE - Friends Edition

**You got the Android Factory zip! 2-minute setup:**

### Fastest Path

1. **Double-click `visual_editor.html`** OR better: run server
   ```bash
   python editor_server.py
   # Open http://localhost:5000 in Chrome
   ```

2. **Design your app** - Drag Text, Buttons, Inputs to phone frame. Add screens with "+ Screen" button. Click widgets to edit them.

3. **Build:**
   - In editor: Click "Save & Auto-Build APK"
   - OR manually: `python builder.py --spec app_spec.json --output ./MyApp --build`
   - OR if no SDK: Open `./MyApp` in Android Studio and hit Run

### What's What

- `README.md` → Full detailed guide (read this after start!)
- `visual_editor.html` → The drag-drop designer
- `builder.py` → The magic that makes APKs
- `app_spec.json` → Your app design file (shareable)
- `GeneratedComposeApp/` → Example built app

### For Non-Technical Friends

If you don't have Python/Android Studio:
1. Install Python from python.org (check "Add to PATH")
2. Install Android Studio from developer.android.com/studio (includes everything needed to build)
3. Then follow 3 steps above

That's it! You can now make native Android apps without writing Java/Kotlin - Python does the heavy lifting into Jetpack Compose.

**Pro tip:** Keep package name unique: `com.yourname.appname` - like `com.jess.pizzaapp`

Have fun! - From Eugene
