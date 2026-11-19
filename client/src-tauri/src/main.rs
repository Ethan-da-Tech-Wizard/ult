// ==============================================================================
// Program: main.rs
// Programmer: Ethan-da-Tech-Wizard
// Last Modified: November 19, 2026
// Purpose: Tauri desktop application entry point and native webview lifecycle container.
//          Initializes the Tauri native runtime, manages OS window decoration and webview
//          IPC messaging bridges, and suppresses terminal console allocation on release builds.
// ==============================================================================

#![cfg_attr(
  all(not(debug_assertions), target_os = "windows"),
  windows_subsystem = "windows"
)]

/// Native desktop application bootstrap initializing Tauri webview runtime.
fn main() {
  tauri::Builder::default()
    .run(tauri::generate_context!())
    .expect("error while running tauri application");
}
