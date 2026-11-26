r"""Record the translation take: Rhapsode reads a Spanish translation aloud.

The page shows the four translated lines as text, but translation in Rhapsode is
not a panel you read - it is what the voice speaks when the reading voice is not
the book's language. This boots the app against a throwaway data directory
(the way `scripts/record_demo.py` in the Rhapsode checkout does), sets the voice
to Spanish, presses play, and records the reader while the translation bar shows
each translated sentence and Kokoro reads it.

    set RHAPSODE_ROOT=C:\Apps\rhapsode
    set PLAYWRIGHT_CHANNEL=msedge
    <rhapsode venv python> tools/make_translation_clip.py

Writes `assets/video/translation-demo.mp4` (1280 wide, h264 + aac),
`assets/img/translation-demo-poster.webp` and `docs/translation-take.json`.
The audio is captured the same way the Rhapsode take's is: a WebAudio tap on the
app's own <audio> element, shifted onto the picture by the measured delay.
"""
import argparse
import base64
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RHAPSODE = Path(os.environ.get("RHAPSODE_ROOT", r"C:\Apps\rhapsode"))
OUT_MP4 = ROOT / "assets" / "video" / "translation-demo.mp4"
OUT_POSTER = ROOT / "assets" / "img" / "translation-demo-poster.webp"
OUT_FACTS = ROOT / "docs" / "translation-take.json"

sys.path.insert(0, str(RHAPSODE / "scripts"))

from record_demo import AUDIO_HOOK, link_models  # noqa: E402  the app's own recorder

TITLE = "The Lantern-Keeper's Ledger"
BODY = (
    "The lantern keeper counted the ships that evening, as she had done every "
    "evening for eleven years. Eleven years of masts and fog and the slow bell "
    "of the harbour, and in all that time the ledger had never once written back.\n\n"
    "She kept it the way her grandmother had: a page for every night, the weather "
    "in the margin, the ships in the body, and one line left blank at the foot for "
    "whatever the sea decided.\n"
)
VOICE = "ef_dora"          # Spanish (female), from the 54-voice Kokoro catalogue


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def call(url: str, payload: dict | None = None, method: str | None = None,
         timeout: float = 300.0) -> dict:
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = urllib.request.Request(
        url, data=data, method=method or ("POST" if data else "GET"),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read())


def wait_for_health(base: str, timeout: float = 120.0) -> dict:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            body = call(base + "/api/health")
            if body.get("ok"):
                return body
        except Exception:
            pass
        time.sleep(0.4)
    raise SystemExit("the app never answered /api/health")


def main() -> int:
    parser = argparse.ArgumentParser(description="record the translation take")
    parser.add_argument("--channel", default=os.environ.get("PLAYWRIGHT_CHANNEL", "msedge"))
    parser.add_argument("--width", type=int, default=1440)
    parser.add_argument("--height", type=int, default=980)
    parser.add_argument("--read-seconds", type=float, default=19.0)
    args = parser.parse_args()

    from playwright.sync_api import sync_playwright

    home = Path(tempfile.mkdtemp(prefix="rhapsode-translate-"))
    models = Path(os.environ.get("LOCALAPPDATA", "")) / "Rhapsode" / "models"
    if not (models / "kokoro-v1.0.onnx").exists():
        models = RHAPSODE / "models"
    link_models(home, models, None)
    # The translator lives in the app's real models folder (runtime + a 4.7 GB
    # GGUF). The throwaway home has only the voice weights, and without this the
    # app opens on "download the on-device translator" instead of translating.
    localmt_src = models / "localmt"
    if localmt_src.is_dir():
        target = home / "models" / "localmt"
        if not target.exists():
            subprocess.run(["cmd", "/c", "mklink", "/J", str(target), str(localmt_src)],
                           capture_output=True, text=True)
        print("translator junction:", target.exists(), flush=True)

    port = free_port()
    base = "http://127.0.0.1:%d" % port
    env = {**os.environ, "MURMUR_HOME": str(home), "MURMUR_PORT": str(port),
           "MURMUR_SEMANTIC": "off", "PYTHONIOENCODING": "utf-8"}
    log_path = home / "server.log"
    log = log_path.open("wb")
    server = subprocess.Popen([sys.executable, "-m", "murmur"], cwd=str(RHAPSODE),
                              env=env, stdout=log, stderr=subprocess.STDOUT)
    video_dir = Path(tempfile.mkdtemp(prefix="rhapsode-translate-take-"))
    playwright = None
    browser = None
    try:
        health = wait_for_health(base)
        print("server on %s - voices=%s" % (base, health.get("voices")), flush=True)

        call(base + "/api/docs", {"title": TITLE, "text": BODY})
        # translateAsked stops the first-run translation card from covering the
        # reader; fontSize 26 keeps the page legible once the take is scaled into
        # a 1280-wide video.
        call(base + "/api/settings",
             {"voice": VOICE, "translateToVoice": True, "translateAsked": True,
              "fontSize": 26},
             method="PUT")
        print("voice set to", VOICE, flush=True)

        # The voice model loads on first use and the translator's llama-server has
        # to start (~40 s); both would be dead air inside the take.
        first = call(base + "/api/tts", {"text": BODY.split(". ")[0] + ".", "voice": VOICE})
        print("warm synthesis: translated=%s -> %s error=%s"
              % (first.get("translated"), first.get("targetLang"), first.get("translateError")),
              flush=True)
        if not first.get("translated"):
            raise SystemExit("the first sentence came back untranslated; the take would be English")

        playwright = sync_playwright().start()
        browser = playwright.chromium.launch(headless=True, channel=args.channel,
                                             args=["--hide-scrollbars"])
        context = browser.new_context(
            viewport={"width": args.width, "height": args.height},
            record_video_dir=str(video_dir),
            record_video_size={"width": args.width, "height": args.height},
            device_scale_factor=1,
        )
        context_started = time.time()
        page = context.new_page()
        page.set_default_timeout(45000)
        page.add_init_script(AUDIO_HOOK)
        # The throwaway home has no stills interpreter, so the app offers its
        # "paint manga stills" card mid-take. This is a recording of the reader,
        # not of setup screens: keep the gates invisible (their logic still runs).
        page.add_init_script(
            "document.addEventListener('DOMContentLoaded', () => {"
            "const s = document.createElement('style');"
            "s.textContent = '.first-run { display: none !important; }';"
            "document.head.appendChild(s); });")

        page.goto(base + "/", wait_until="load")
        page.wait_for_selector(".lib-item")
        # If the app still thinks translation needs setting up, decline it rather
        # than let a modal eat the click on play.
        try:
            if page.is_visible("#translateSetup"):
                page.evaluate("document.querySelectorAll('.first-run').forEach(el => { el.hidden = true; })")
                print("hid the translation setup card", flush=True)
        except Exception:
            pass
        page.wait_for_timeout(1600)
        page.screenshot(path=str(ROOT / "docs" / "translation-take-library.png"))

        page.locator(".lib-item", has_text="Lantern").first.click()
        page.wait_for_selector("#reader .unit, #reader p")
        page.wait_for_timeout(1500)

        page.click("#playBtn")
        page.wait_for_selector(".unit.is-current", timeout=90000)
        # the bar appears once the first sentence comes back translated
        page.wait_for_selector("#translationBar:not([hidden])", timeout=90000)
        page.wait_for_timeout(1200)
        page.screenshot(path=str(ROOT / "docs" / "translation-take-reading.png"))
        page.wait_for_timeout(int(args.read_seconds * 1000))
        page.click("#playBtn")

        chrome_text = page.eval_on_selector(
            "#translationLang", "el => el.textContent")
        shown = page.eval_on_selector("#translationText", "el => el.textContent")
        print("translation bar:", chrome_text, "|", shown[:80], flush=True)

        sound = None
        try:
            sound = page.evaluate("window.__demoAudioStop()")
        except Exception as exc:  # noqa: BLE001
            print("audio capture failed (%s); the take stays silent" % exc)

        video = page.video
        context.close()
        recorded = Path(video.path())
        browser.close()
        browser = None
        playwright.stop()
        playwright = None
    finally:
        server.terminate()
        try:
            server.wait(timeout=15)
        except Exception:
            server.kill()
        log.close()

    raw = video_dir / "take.webm"
    shutil.copyfile(recorded, raw)
    ffmpeg = shutil.which("ffmpeg") or "ffmpeg"
    OUT_MP4.parent.mkdir(parents=True, exist_ok=True)
    silent = video_dir / "take-silent.mp4"
    result = subprocess.run(
        [ffmpeg, "-y", "-i", str(raw), "-vf", "scale=1280:-2", "-c:v", "libx264",
         "-preset", "slow", "-crf", "30", "-pix_fmt", "yuv420p",
         "-movflags", "+faststart", "-an", str(silent)],
        capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr[-1500:])
        raise SystemExit("ffmpeg could not encode the take")

    if sound and sound.get("base64"):
        audio_raw = video_dir / "take-audio.webm"
        audio_raw.write_bytes(base64.b64decode(sound["base64"]))
        delay = max(0.0, sound["startEpochMs"] / 1000.0 - context_started)
        mux = subprocess.run(
            [ffmpeg, "-y", "-i", str(silent), "-i", str(audio_raw),
             "-filter_complex", "[1:a]adelay=%d:all=1,apad[a]" % int(delay * 1000),
             "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "96k",
             "-ac", "1", "-shortest", "-movflags", "+faststart", str(OUT_MP4)],
            capture_output=True, text=True)
        if mux.returncode != 0:
            print(mux.stderr[-1200:])
            shutil.copyfile(silent, OUT_MP4)
            print("mux failed; the deliverable is silent")
        else:
            print("voice starts %.2fs into the take" % delay, flush=True)
    else:
        shutil.copyfile(silent, OUT_MP4)

    subprocess.run([ffmpeg, "-y", "-ss", "6.0", "-i", str(OUT_MP4), "-frames:v", "1",
                    "-c:v", "libwebp", "-quality", "84", str(OUT_POSTER)],
                   capture_output=True, text=True)

    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration,size",
         "-show_entries", "stream=codec_name,width,height", "-of", "default=nw=1",
         str(OUT_MP4)], capture_output=True, text=True)
    print(probe.stdout.strip())
    OUT_FACTS.write_text(json.dumps({
        "voice": VOICE,
        "title": TITLE,
        "bar_language": chrome_text,
        "bar_text": shown,
        "seconds": round(time.time() - context_started, 1),
    }, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("demo: %d KB | poster: %d KB" % (OUT_MP4.stat().st_size // 1024,
                                           OUT_POSTER.stat().st_size // 1024))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
