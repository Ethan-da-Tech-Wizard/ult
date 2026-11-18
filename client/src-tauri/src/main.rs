// Program: ult - main.rs
// Programmer: Ethan-da-Tech-Wizard (written with Claude, an AI assistant)
// Last Modified: 2026-11-18
// Purpose: Entry point of the Tauri desktop shell that wraps the web client in a native window.
// On Windows release builds, hide the extra console window.
#![cfg_attr(
  all(not(debug_assertions), target_os = "windows"),
  windows_subsystem = "windows"
)]

/// Build and run the Tauri application using the context generated from the project's Tauri configuration; panics with a message if it cannot start.
fn main() {
  tauri::Builder::default()
    .run(tauri::generate_context!())
    .expect("error while running tauri application");
}
