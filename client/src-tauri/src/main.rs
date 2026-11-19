// ==============================================================================
// Program: main.rs
// Programmer: Ethan-da-Tech-Wizard
// Last Modified: November 19, 2026
// Purpose: Tauri desktop application entry point and native webview lifecycle container.
//          Initializes the Tauri native runtime, manages OS window decoration and webview
//          IPC messaging bridges, and suppresses terminal console allocation on release builds.
// ==============================================================================

// How this file fits the app: optional native desktop shell around the game. Tauri opens a window whose
// web content is the client folder (client/index.html + app.js, configured in tauri.conf.json); the Python
// server (server/main.py) must be running separately on 127.0.0.1:8000 because the game's API lives there.
// This is the entire Rust side: there is no custom command, so the web page never calls Rust. Build/run
// with the Tauri CLI from client/ (needs the Rust toolchain; not part of CI). No unit tests exist for this
// file.
// On Windows release builds the attribute below selects the GUI subsystem so no black console window opens
// behind the game; in debug builds (and on other systems) it is inactive, so log output stays visible.
#![cfg_attr(
  all(not(debug_assertions), target_os = "windows"),
  windows_subsystem = "windows"
)]

/// Native desktop application bootstrap initializing Tauri webview runtime.
fn main() {
  // `generate_context!()` embeds tauri.conf.json (window size, allowed APIs, frontend path) at compile
  // time; `run` starts the event loop and blocks until the window is closed. A failure (for example a
  // missing webview runtime) is turned into a panic with this message.
  tauri::Builder::default()
    .run(tauri::generate_context!())
    .expect("error while running tauri application");
}
