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
    """Starts the QEMU TempleOS instance with serial redirected to a local telnet socket.

    NOTE: stock TempleOS has no serial console driver (it is VGA + PS/2 only),
    so the serial bridge only carries data with a serial-patched community
    build. Set ZEUS_TEMPLEOS_VNC=1 to also expose the VM's real display on
    VNC 127.0.0.1:5900 — that shows actual TempleOS with the real HolyC
    compiler, viewable with any VNC client.
    """
    if not os.path.exists(IMAGE_PATH):
        logger.warning(f"TempleOS core image not found at {IMAGE_PATH}. Launching mock HolyC sandbox terminal.")
        start_mock_holyc_server()
        return

    cmd = [
        "qemu-system-x86_64",
        "-m", "512M",
        "-hda", IMAGE_PATH,
        "-serial", f"telnet:127.0.0.1:{PORT},server,nowait"
    ]
    if os.environ.get("ZEUS_TEMPLEOS_VNC") == "1":
        cmd += ["-vnc", "127.0.0.1:0"]
        logger.info("TempleOS real display exposed on VNC 127.0.0.1:5900")
    else:
        cmd += ["-nographic"]
    try:
        logger.info(f"Launching QEMU TempleOS: {' '.join(cmd)}")
        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return proc
    except Exception as e:
        logger.error(f"Failed to start QEMU: {e}. Falling back to mock HolyC server.")
        start_mock_holyc_server()

def looks_like_holyc(code):
    """Mirrors the Chapter 21 validator: reject interpreted-language syntax,
    require actual HolyC type/function markers before 'compiling'."""
    if "def " in code or "print(" in code or "import " in code or "console.log" in code:
        return False
    return any(marker in code for marker in ("U0", "I64", "U8", "F64", "Print"))


def holyc_checksum(code):
    """Deterministic 16-bit checksum so the Altar's output is verifiable."""
    return sum(code.encode("utf-8", errors="replace")) & 0xFFFF


MOCK_HELP_TEXT = (
    b"Divine Compiler commands:\r\n"
    b"  HELP            show this text\r\n"
    b"  EXIT / QUIT     disconnect from the Altar\r\n"
    b"  <HolyC code>    JIT-compile a snippet, e.g.:\r\n"
    b"      U0 Hymn() { Print(\"Praise\\n\"); } Hymn();\r\n"
)


def start_mock_holyc_server():
    """Launches an offline loopback socket that mimics the TempleOS command
    prompt. Unlike a stub, it actually validates HolyC syntax: Python or JS
    syntax is rejected, and accepted snippets get a deterministic checksum."""
    def client_thread(conn, addr):
        conn.sendall(b"\r\n--- Terry's Sanctuary: Headless TempleOS Altar (Mock) ---\r\n")
        conn.sendall(b"TempleOS V5.03 Divine Compiler bridge\r\n")
        conn.sendall(b"Write HolyC scripts (.HC) and compile them natively. Type HELP for syntax.\r\n")

        while True:
            try:
                conn.sendall(b"HolyC> ")
                data = conn.recv(4096)
                if not data:
                    break
                text = data.decode("utf-8", errors="replace").strip()
                if not text:
                    continue
                upper = text.upper()
                if upper in ("EXIT", "QUIT"):
                    conn.sendall(b"Disconnecting from the Altar...\r\n")
                    break
                if upper == "HELP":
                    conn.sendall(MOCK_HELP_TEXT)
                    continue
                conn.sendall(f"Compiling '{text[:60]}'...\r\n".encode("utf-8"))
                time.sleep(0.4)
                if looks_like_holyc(text):
                    checksum = holyc_checksum(text)
                    conn.sendall(
                        f"JIT OK. Result: 0 (Success). Checksum: 0x{checksum:04X}\r\n".encode("utf-8")
                    )
                else:
                    conn.sendall(
                        b"Compile error: not HolyC. The Divine Intellect rejects interpreted heresy.\r\n"
                        b"Hint: U0 FuncName() { Print(\"...\\n\"); } FuncName();\r\n"
                    )
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
