import os
import subprocess
import socket
import threading
import time
import logging

logger = logging.getLogger("QemuLauncher")

IMAGE_PATH = os.path.join("save_data", "templeos_core.img")
PORT = 4444

def start_qemu():
    """Starts the QEMU TempleOS instance with serial redirected to a local telnet socket."""
    if not os.path.exists(IMAGE_PATH):
        logger.warning(f"TempleOS core image not found at {IMAGE_PATH}. Launching mock HolyC sandbox terminal.")
        start_mock_holyc_server()
        return

    cmd = [
        "qemu-system-x86_64",
        "-hda", IMAGE_PATH,
        "-nographic",
        "-serial", f"telnet:127.0.0.1:{PORT},server,nowait"
    ]
    try:
        logger.info(f"Launching QEMU TempleOS: {' '.join(cmd)}")
        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return proc
    except Exception as e:
        logger.error(f"Failed to start QEMU: {e}. Falling back to mock HolyC server.")
        start_mock_holyc_server()

def start_mock_holyc_server():
    """Launches an offline loopback socket that mimics the TempleOS command prompt for local coding tests."""
    def client_thread(conn, addr):
        conn.sendall(b"\r\n--- Terry's Sanctuary: Headless TempleOS Altar (Mock) ---\r\n")
        conn.sendall(b"TempleOS V5.03\r\n")
        conn.sendall(b"Write HolyC scripts (.HC) and compile them natively.\r\n")

        while True:
            try:
                conn.sendall(b"HolyC> ")
                data = conn.recv(1024)
                if not data:
                    break
                text = data.decode("utf-8", errors="replace").strip()
                if text == "exit" or text == "quit":
                    conn.sendall(b"Disconnecting...\r\n")
                    break
                elif text:
                    # Simple mock parser executing commands
                    conn.sendall(f"Compiling '{text}'...\r\n".encode("utf-8"))
                    time.sleep(0.5)
                    conn.sendall(b"Result: 0 (Success) - Verification passed.\r\n")
            except Exception:
                break
        conn.close()

    def server_loop():
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Bind strictly to local loopback interface
        try:
            server_socket.bind(("127.0.0.1", PORT))
            server_socket.listen(5)
            logger.info(f"Mock HolyC server bound to 127.0.0.1:{PORT}")
            while True:
                conn, addr = server_socket.accept()
                t = threading.Thread(target=client_thread, args=(conn, addr), daemon=True)
                t.start()
        except Exception as e:
            logger.error(f"Mock server socket error: {e}")

    t = threading.Thread(target=server_loop, daemon=True)
    t.start()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    start_qemu()
    # Keep main thread alive
    while True:
        time.sleep(1)
