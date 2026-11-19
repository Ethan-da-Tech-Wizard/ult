# ==============================================================================
# Program: qemu_launcher.py
# Programmer: Ethan-da-Tech-Wizard
# Last Modified: November 19, 2026
# Purpose: Virtual machine orchestrator managing headless QEMU instances and serial I/O pipelines.
#          Provisions hardware emulation parameters (512MB RAM, disk images, telnet serial socket),
#          handles VNC display bindings, and implements a multi-threaded mock HolyC telnet server
#          fall-back with syntax verification and deterministic 16-bit checksum calculation.
# ==============================================================================

# How this file fits the app: started once from the lifespan hook of server/main.py to provide the Chapter 21
# "Altar of TempleOS" console. The browser connects to /ws/templeos, which proxies to TCP 127.0.0.1:4444.
# Two back ends supply that port: real QEMU running a TempleOS disk image (save_data/templeos_core.img, built
# by setup/build_templeos_img.sh) with its serial port exposed as a telnet server, or an in-process mock
# "HolyC" server that
# recognises HolyC-looking text and returns a fake compile result plus a checksum. The mock is what runs on
# most machines because the image is large and optional.
# Limits: stock TempleOS does not drive a serial port, so real-QEMU output only appears with a serial-patched
# build; the mock's "compiler" is a keyword check, not a real HolyC compiler.
import logging
import os
import socket
import subprocess
import threading
import time

logger = logging.getLogger("QemuLauncher")

# Relative to the current working directory (start from the repo root). The telnet port is fixed; main.py
# connects to the same number.
# Virtual drive image destination and loopback telnet port
IMAGE_PATH = os.path.join("save_data", "templeos_core.img")
PORT = 4444


# Returns the QEMU Popen handle or None (mock started). QEMU is spawned and not waited on, so it keeps running
# for the life of the server; nothing here stops it at shutdown (it is orphaned when the server exits unless
# the OS cleans it up).
def start_qemu():
    """Starts the QEMU TempleOS instance with serial redirected to a local telnet socket.

    Architecture & Concurrency:
      - Validates disk image availability before invoking hypervisor process.
      - Stock TempleOS has no serial console driver (it is VGA + PS/2 only);
        the serial bridge only carries data with a serial-patched community build.
      - Set ZEUS_TEMPLEOS_VNC=1 to expose the VM display on VNC 127.0.0.1:5900.
      - If image is missing or QEMU fails to launch, gracefully falls back to the
        in-process multi-threaded HolyC mock telnet server.
    """
    if not os.path.exists(IMAGE_PATH):
        logger.warning(f"TempleOS core image not found at {IMAGE_PATH}. Launching mock HolyC sandbox terminal.")
        start_mock_holyc_server()
        return None

    # -m 512M gives the guest 512 MB RAM (TempleOS needs little). `-serial telnet:...,server,nowait` makes
    # QEMU listen on the port without blocking boot until a client connects.
    # Assemble QEMU hardware virtualization parameters
    cmd = [
        "qemu-system-x86_64",
        "-m", "512M",
        "-hda", IMAGE_PATH,
        "-serial", f"telnet:127.0.0.1:{PORT},server,nowait",
    ]

    # Headless by default (-nographic). ZEUS_TEMPLEOS_VNC=1 instead exposes the guest screen on VNC
    # 127.0.0.1:5900 (display :0 = port 5900) for debugging.
    # Conditionally bind VNC display or enforce headless execution
    if os.environ.get("ZEUS_TEMPLEOS_VNC") == "1":
        cmd += ["-vnc", "127.0.0.1:0"]
        logger.info("TempleOS real display exposed on VNC 127.0.0.1:5900")
    else:
        cmd += ["-nographic"]

    try:
        logger.info(f"Launching QEMU TempleOS: {' '.join(cmd)}")

        # DEVNULL discards QEMU output; if the pipes were left open and unread the child could block when a
        # buffer fills.
        # Spawn child process with suppressed standard streams to prevent pipe buffer blocks
        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return proc
    except Exception as e:
        logger.error(f"Failed to start QEMU: {e}. Falling back to mock HolyC server.")
        start_mock_holyc_server()
        return None


# Heuristic used by the mock (and mirrored by the chapter 21 validator): reject obviously interpreted
# languages, then require at least one HolyC type/function marker. Intentionally simple; it accepts any text
# containing those tokens.
def looks_like_holyc(code):
    """Validates submitted code against HolyC linguistic syntax conventions.

    Mirrors Chapter 21 requirements: rejects interpreted syntax (Python, JS)
    and enforces static HolyC primitive types or function call signatures.

    Args:
        code: Source text snippet submitted over the telnet stream.

    Returns:
        True if text exhibits HolyC linguistic tokens; False otherwise.
    """
    # Reject high-level interpreted keywords
    if "def " in code or "print(" in code or "import " in code or "console.log" in code:
        return False
    # Enforce Presence of canonical HolyC primitives
    return any(marker in code for marker in ("U0", "I64", "U8", "F64", "Print"))


# Sum of all UTF-8 bytes modulo 65536 ("& 0xFFFF"). Deterministic so the chapter 21 puzzle can predict the
# value shown by the mock; it is NOT a cryptographic or CRC checksum.
def holyc_checksum(code):
    """Computes a deterministic 16-bit summation checksum over UTF-8 encoded text.

    Args:
        code: Submitted source string.

    Returns:
        16-bit unsigned integer checksum used for Altar compilation verification.
    """
    return sum(code.encode("utf-8", errors="replace")) & 0xFFFF


# Text printed for HELP in the mock console (bytes with \r\n because telnet clients expect CRLF).
# Interactive terminal instructional banner for mock telnet sessions
MOCK_HELP_TEXT = (
    b"Divine Compiler commands:\r\n"
    b"  HELP            show this text\r\n"
    b"  EXIT / QUIT     disconnect from the Altar\r\n"
    b"  <HolyC code>    JIT-compile a snippet, e.g.:\r\n"
    b"      U0 Hymn() { Print(\"Praise\\n\"); } Hymn();\r\n"
)


# Starts the listener thread and returns immediately. Binding failures (port already in use) are logged and
# the thread ends, so the console then simply fails to connect.
def start_mock_holyc_server():
    """Launches an offline loopback socket server that mimics the TempleOS command prompt.

    Concurrency Design:
      - Binds to 127.0.0.1:4444 with SO_REUSEADDR enabled.
      - Spawns a dedicated daemon thread for the listening socket loop.
      - Spawns an isolated daemon client thread per incoming connection.
      - Performs immediate HolyC syntax validation and emits compilation responses.
    """

    # One thread per connection (daemon threads, so they never keep the server alive at exit); each thread
    # runs a simple prompt/response loop.
    def client_thread(conn, addr):
        """Dedicated connection handler thread for each connected telnet client."""
        try:
            # Emit initial connection banner
            conn.sendall(b"\r\n--- Terry's Sanctuary: Headless TempleOS Altar (Mock) ---\r\n")
            conn.sendall(b"TempleOS V5.03 Divine Compiler bridge\r\n")
            conn.sendall(b"Write HolyC scripts (.HC) and compile them natively. Type HELP for syntax.\r\n")

            while True:
                # Prompt user and wait for line input
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

                # 0.4 s sleep imitates compiler latency so the puzzle feels real; it only blocks this client's
                # thread.
                # Simulate JIT compilation latency
                conn.sendall(f"Compiling '{text[:60]}'...\r\n".encode("utf-8"))
                time.sleep(0.4)

                # Validate syntax and emit compilation result
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
        except Exception as exc:
            logger.debug(f"Client session error ({addr}): {exc}")
        finally:
            conn.close()

    # Accept loop. SO_REUSEADDR lets the server restart immediately without waiting for the old socket's
    # TIME_WAIT to expire. Bound to loopback only.
    def server_loop():
        """Accept loop running within a background daemon thread."""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Bind strictly to local loopback interface for security
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

    # Launch daemon listener thread
    t = threading.Thread(target=server_loop, daemon=True)
    t.start()


# Standalone mode for manual testing: `python server/qemu_launcher.py` then `telnet 127.0.0.1 4444`.
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    start_qemu()
    # Keep main thread alive during standalone manual execution
    while True:
        time.sleep(1)
