#!/usr/bin/env python3
"""
Android App Catalyst V3 - Jetpack Compose Edition
Generates 100% Modern Compose + Material3 Native Android Apps

- Reads spec from visual_editor (JSON) or app_spec.py
- Generates Compose project (no XML layouts!)
- Auto-builds APK if SDK available
"""
import os, json, shutil, argparse, subprocess, importlib.util
from pathlib import Path

def load_config(spec_path: Path):
    if not spec_path or not spec_path.exists():
        # Try JSON first, then PY
        json_path = Path("app_spec.json")
        if json_path.exists():
            return json.loads(json_path.read_text())
        from app_spec import APP_CONFIG
        return APP_CONFIG
    if spec_path.suffix == '.json':
        return json.loads(spec_path.read_text())
    elif spec_path.suffix == '.py':
        spec = importlib.util.spec_from_file_location("app_spec", spec_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod.APP_CONFIG
    else:
        raise ValueError("Spec must be .py or .json")

# --- GRADLE TEMPLATES ---
BUILD_GRADLE_PROJECT = """// Top-level build file
plugins {
    id 'com.android.application' version '8.2.0' apply false
    id 'org.jetbrains.kotlin.android' version '1.9.10' apply false
}
"""

SETTINGS_GRADLE = """pluginManagement {
    repositories { google(); mavenCentral(); gradlePluginPortal() }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories { google(); mavenCentral() }
}
rootProject.name = "__APP_NAME__"
include ':app'
"""

BUILD_GRADLE_APP = """plugins {
    id 'com.android.application'
    id 'org.jetbrains.kotlin.android'
}

android {
    namespace '__PACKAGE__'
    compileSdk 34
    defaultConfig {
        applicationId "__PACKAGE__"
        minSdk 24
        targetSdk 34
        versionCode __VERSION_CODE__
        versionName "__VERSION_NAME__"
        testInstrumentationRunner "androidx.test.runner.AndroidJUnitRunner"
        vectorDrawables { useSupportLibrary = true }
    }
    buildTypes {
        release {
            minifyEnabled false
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }
    }
    compileOptions {
        sourceCompatibility JavaVersion.VERSION_1_8
        targetCompatibility JavaVersion.VERSION_1_8
    }
    kotlinOptions { jvmTarget = '1.8' }
    buildFeatures { compose true }
    composeOptions { kotlinCompilerExtensionVersion = '1.5.4' }
    packaging { resources { excludes += '/META-INF/{AL2.0,LGPL2.1}' } }
}

dependencies {
    implementation 'androidx.core:core-ktx:1.12.0'
    implementation 'androidx.lifecycle:lifecycle-runtime-ktx:2.6.2'
    implementation 'androidx.activity:activity-compose:1.8.1'
    implementation platform('androidx.compose:compose-bom:2023.10.01')
    implementation 'androidx.compose.ui:ui'
    implementation 'androidx.compose.ui:ui-graphics'
    implementation 'androidx.compose.ui:ui-tooling-preview'
    implementation 'androidx.compose.material3:material3'
    implementation 'androidx.compose.material:material-icons-extended'
    implementation 'androidx.navigation:navigation-compose:2.7.5'
    implementation 'androidx.compose.material:material:1.5.4'
}
"""

GRADLE_PROPS = """org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
android.useAndroidX=true
android.nonTransitiveRResources=true
"""

MANIFEST = """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools">
    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:supportsRtl="true"
        android:theme="@style/Theme.__THEME__"
        tools:targetApi="31">
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:label="@string/app_name"
            android:theme="@style/Theme.__THEME__">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
"""

COLOR_KT = """package __PACKAGE__.ui.theme
import androidx.compose.ui.graphics.Color
val Purple80 = Color(0xFFD0BCFF)
val PurpleGrey80 = Color(0xFFCCC2DC)
val Pink80 = Color(0xFFEFB8C8)
val Purple40 = Color(0xFF6650a4)
val PurpleGrey40 = Color(0xFF625b71)
val Pink40 = Color(0xFF7D5260)
val Primary = Color(0xFF__PRIMARY_HEX__)
val PrimaryDark = Color(0xFF__PRIMARY_DARK_HEX__)
"""

THEME_KT = """package __PACKAGE__.ui.theme
import android.app.Activity
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.SideEffect
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.platform.LocalView
import androidx.core.view.WindowCompat

private val DarkColorScheme = darkColorScheme(
    primary = Primary, secondary = PurpleGrey80, tertiary = Pink80
)
private val LightColorScheme = lightColorScheme(
    primary = Primary, secondary = PurpleGrey40, tertiary = Pink40
)

@Composable
fun __THEME__Theme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit
) {
    val colorScheme = if (darkTheme) DarkColorScheme else LightColorScheme
    val view = LocalView.current
    if (!view.isInEditMode) {
        SideEffect {
            val window = (view.context as Activity).window
            window.statusBarColor = colorScheme.primary.toArgb()
            WindowCompat.getInsetsController(window, view).isAppearanceLightStatusBars = darkTheme
        }
    }
    MaterialTheme(colorScheme = colorScheme, content = content)
}
"""

TYPE_KT = """package __PACKAGE__.ui.theme
import androidx.compose.material3.Typography
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.sp
val Typography = Typography(
    bodyLarge = TextStyle(fontFamily = FontFamily.Default, fontWeight = FontWeight.Normal, fontSize = 16.sp, lineHeight = 24.sp, letterSpacing = 0.5.sp)
)
"""

# --- COMPOSE CODE GENERATOR ---
def widget_to_compose(widget, screen_state_vars):
    t = widget.get("type","TextView")
    wid = widget.get("id","widget")
    text = widget.get("text","").replace('"','\\"')
    
    if t == "TextView":
        return f'            Text(text = "{text}", style = MaterialTheme.typography.headlineSmall, textAlign = TextAlign.Center, modifier = Modifier.fillMaxWidth().padding(8.dp))'
    
    elif t == "Button":
        action = widget.get("action","")
        onclick = ""
        if action.startswith("showToast:"):
            msg = action.split(":",1)[1].replace('"','\\"')
            onclick = f'Toast.makeText(context, "{msg}", Toast.LENGTH_SHORT).show()'
        elif action.startswith("navigate:"):
            target = action.split(":",1)[1].replace("Activity","")
            onclick = f'navController.navigate("{target}")'
        elif action == "finish":
            onclick = f'(context as? Activity)?.finish()'
        else:
            # auto-navigate if more than 1 screen, otherwise toast
            onclick = f'Toast.makeText(context, "{text} clicked", Toast.LENGTH_SHORT).show()'
        
        return f'''            Button(onClick = {{ {onclick} }}, modifier = Modifier.fillMaxWidth().padding(vertical = 6.dp)) {{
                Text("{text}")
            }}'''
    
    elif t == "EditText":
        # Track state var
        var_name = wid + "State"
        if var_name not in screen_state_vars:
            screen_state_vars.append(var_name)
        hint = widget.get("hint","Enter text").replace('"','\\"')
        return f'''            OutlinedTextField(value = {var_name}, onValueChange = {{ {var_name} = it }}, label = {{ Text("{hint}") }}, modifier = Modifier.fillMaxWidth().padding(vertical = 6.dp))'''
    
    elif t == "ImageView":
        return f'''            Image(painter = painterResource(id = R.mipmap.ic_launcher), contentDescription = null, modifier = Modifier.size(120.dp).clip(CircleShape), contentScale = ContentScale.Crop)'''
    
    elif t == "Switch":
        var_name = wid + "SwitchState"
        if var_name not in screen_state_vars:
            screen_state_vars.append(var_name+"_bool")
        # simplify: we'll handle separately
        return f'''            Row(modifier = Modifier.fillMaxWidth().padding(8.dp), verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.SpaceBetween) {{
                Text("{text}")
                var {wid}Checked by remember {{ mutableStateOf(false) }}
                Switch(checked = {wid}Checked, onCheckedChange = {{ {wid}Checked = it }})
            }}'''
    
    elif t == "Spacer":
        h = widget.get("height","24dp").replace("dp","").replace("px","")
        try:
            hd = int(h)
        except:
            hd = 24
        return f'            Spacer(modifier = Modifier.height({hd}.dp))'
    
    else:
        return f'            Text("Unknown widget {t}")'

def generate_compose_screens(config):
    package = config["package_name"]
    screens = config["screens"]
    
    # Collect composables
    composables = []
    routes = []
    
    for screen in screens:
        name = screen["name"]
        route = name  # use name as route
        routes.append(route)
        activity_name = screen["activity_name"].replace("Activity","")  # Home, About, etc.
        # For NavHost compatibility, use name directly
        state_vars = []  # track EditText states
        
        widgets_compose = []
        for w in screen.get("widgets",[]):
            # Pre-collect EditText state vars
            if w.get("type")=="EditText":
                var_name = w.get("id")+"State"
                if var_name not in state_vars:
                    state_vars.append(var_name)
        
        # Generate state declarations
        state_decls = ""
        for sv in state_vars:
            state_decls += f'    var {sv} by remember {{ mutableStateOf("") }}\n'
        
        # Generate widgets
        widgets_code = "\n".join([widget_to_compose(w, []) for w in screen.get("widgets",[])])
        
        # Build composable
        comp = f'''
@Composable
fun {activity_name}Screen(navController: NavHostController) {{
    val context = LocalContext.current
{state_decls}
    Column(
        modifier = Modifier.fillMaxSize().padding(16.dp).verticalScroll(rememberScrollState()),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Top
    ) {{
        Text(text = "{name}", style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold, modifier = Modifier.padding(bottom = 16.dp))
{widgets_code}
    }}
}}
'''
        composables.append(comp)
    
    # Build NavHost + MainActivity
    nav_graph = ""
    for screen in screens:
        route = screen["name"]
        func_name = screen["activity_name"].replace("Activity","") + "Screen"
        nav_graph += f'        composable("{route}") {{ {func_name}(navController) }}\n'
    
    start_dest = screens[0]["name"] if screens else "Home"
    
    main_activity = f'''package {package}

import android.app.Activity
import android.os.Bundle
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.Image
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import {package}.ui.theme.{config["app_name"].replace(" ","").replace("-","") or "MyApp"}Theme

class MainActivity : ComponentActivity() {{
    override fun onCreate(savedInstanceState: Bundle?) {{
        super.onCreate(savedInstanceState)
        setContent {{
            {config["app_name"].replace(" ","").replace("-","") or "MyApp"}Theme {{
                Surface(modifier = Modifier.fillMaxSize(), color = MaterialTheme.colorScheme.background) {{
                    AppNavHost()
                }}
            }}
        }}
    }}
}}

@Composable
fun AppNavHost() {{
    val navController = rememberNavController()
    NavHost(navController = navController, startDestination = "{start_dest}") {{
{nav_graph}
    }}
}}

{"".join(composables)}
'''
    return main_activity

def create_project(config, output_dir: Path):
    output_dir = Path(output_dir)
    if output_dir.exists():
        shutil.rmtree(output_dir)
    
    pkg = config["package_name"]
    pkg_path = pkg.replace(".","/")
    theme_name = "".join([p.capitalize() for p in config["app_name"].split() if p.isalnum()]) or "MyApp"
    primary_hex = config.get("primary_color","#6200EE").lstrip("#")
    primary_dark_hex = config.get("primary_dark_color","#3700B3").lstrip("#")
    
    # dirs
    java_dir = output_dir / f"app/src/main/java/{pkg_path}"
    theme_dir = java_dir / "ui/theme"
    res_values = output_dir / "app/src/main/res/values"
    res_mipmap = output_dir / "app/src/main/res/mipmap-hdpi"
    wrapper_dir = output_dir / "gradle/wrapper"
    
    for d in [java_dir, theme_dir, res_values, res_mipmap, wrapper_dir]:
        d.mkdir(parents=True, exist_ok=True)
    
    # gradle
    (output_dir / "build.gradle").write_text(BUILD_GRADLE_PROJECT)
    (output_dir / "settings.gradle").write_text(SETTINGS_GRADLE.replace("__APP_NAME__", config["app_name"]))
    (output_dir / "app/build.gradle").write_text(
        BUILD_GRADLE_APP.replace("__PACKAGE__", pkg)
        .replace("__VERSION_CODE__", str(config.get("version_code",1)))
        .replace("__VERSION_NAME__", str(config.get("version_name","1.0")))
    )
    (output_dir / "app/proguard-rules.pro").write_text("-keep class androidx.compose.** { *; }")
    (wrapper_dir / "gradle-wrapper.properties").write_text("distributionBase=GRADLE_USER_HOME\ndistributionPath=wrapper/dists\ndistributionUrl=https\\://services.gradle.org/distributions/gradle-8.2-bin.zip\nzipStoreBase=GRADLE_USER_HOME\nzipStorePath=wrapper/dists\n")
    (output_dir / "gradle.properties").write_text(GRADLE_PROPS)
    (output_dir / "gradlew").write_text("#!/bin/sh\nexec gradle \"$@\"\n")
    try: os.chmod(output_dir / "gradlew", 0o775)
    except: pass
    
    # manifest + res
    (output_dir / "app/src/main/AndroidManifest.xml").write_text(
        MANIFEST.replace("__THEME__", theme_name)
    )
    (res_values / "strings.xml").write_text(f'<resources><string name="app_name">{config["app_name"]}</string></resources>')
    (res_values / "colors.xml").write_text(f'<resources><color name="colorPrimary">{config.get("primary_color")}</color></resources>')
    (res_values / "themes.xml").write_text(f'<resources><style name="Theme.{theme_name}" parent="Theme.Material3.DayNight.NoActionBar" /></resources>')
    
    # theme kt
    (theme_dir / "Color.kt").write_text(
        COLOR_KT.replace("__PACKAGE__", pkg)
        .replace("__PRIMARY_HEX__", primary_hex)
        .replace("__PRIMARY_DARK_HEX__", primary_dark_hex)
    )
    (theme_dir / "Theme.kt").write_text(
        THEME_KT.replace("__PACKAGE__", pkg).replace("__THEME__", theme_name)
    )
    (theme_dir / "Type.kt").write_text(TYPE_KT.replace("__PACKAGE__", pkg))
    
    # MainActivity with Compose
    compose_code = generate_compose_screens(config)
    (java_dir / "MainActivity.kt").write_text(compose_code)
    
    print(f"✅ Compose project generated: {output_dir.resolve()}")
    print(f"   Screens: {len(config['screens'])} -> Compose NavHost")
    print(f"   Package: {pkg}")
    return output_dir

def attempt_build(project_dir: Path):
    project_dir = Path(project_dir).resolve()
    if not shutil.which("java"):
        print("❌ Java not found. Install JDK 17+ to auto-build.")
        return False
    gradlew = project_dir / "gradlew"
    cmd = ["./gradlew","assembleDebug"] if gradlew.exists() else (["gradle","assembleDebug"] if shutil.which("gradle") else None)
    if not cmd:
        print("❌ Gradle not found")
        return False
    print(f"🔨 Building {project_dir.name} with {' '.join(cmd)}...")
    try:
        proc = subprocess.run(cmd, cwd=str(project_dir), capture_output=True, text=True, timeout=600)
        if proc.returncode==0:
            apk = project_dir / "app/build/outputs/apk/debug/app-debug.apk"
            if apk.exists():
                dist = Path.cwd() / "dist"
                dist.mkdir(exist_ok=True)
                dest = dist / f"{project_dir.name}.apk"
                shutil.copy(apk, dest)
                print(f"✅ APK built: {dest.resolve()} ({dest.stat().st_size/1_000_000:.1f} MB)")
                return True
            else:
                apks = list((project_dir/"app/build").rglob("*.apk"))
                if apks:
                    print(f"✅ Found APKs: {apks}")
                    return True
        else:
            print(f"Build log tail:\n{proc.stdout[-2000:]}\n{proc.stderr[-2000:]}")
    except Exception as e:
        print(f"Build error: {e}")
    return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", "-s", default="app_spec.json")
    parser.add_argument("--output", "-o", default="./GeneratedComposeApp")
    parser.add_argument("--build", "-b", action="store_true")
    args = parser.parse_args()
    
    config = load_config(Path(args.spec))
    out = create_project(config, Path(args.output))
    if args.build:
        attempt_build(out)
    else:
        print("\nTip: Add --build to compile APK, or open in Android Studio")
        print(f"  python builder.py --spec {args.spec} --build")
