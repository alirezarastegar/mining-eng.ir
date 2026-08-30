#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
import struct
import wave
from pathlib import Path

EXPECTED = {
    "package.json": "37028b86a78b374ed66a0e8f4837b1f1e180758d90dec5418a26734a12acceea",
    "main.js": "d2a959f3ac668a233dc75e0026cd9c5ba8826176edfab5915771e7b70f674119",
    "renderer/app.js": "b8a6e7e8d10d1b62c71d3a0ea27bfcf0cd0b0190b4745084d96a77a0caeef1b9",
    "renderer/app.css": "2ccb240f52e4f72c1717a5fef373f7f453218d558ecd0562a2a820cc3e77dfe9",
    "renderer/index.html": "3a7a34c7c47b1e7790cf753042969bc5fa9350d6863507c8999a8ffc3ab893ee",
    "tests/desktop_contract_test.js": "c14ccc5334b475325d858a08bf9346846bb65619e8908fbab49aa574b087890e",
    "installer/main.go": "b61c79f44fbd3e29e1f0de3a677d001d3a6375e1c38088d99db5f857a839f836",
    "assets/icons/planjoy.png": "27cf729e3dd434684f2592994ef93c8c7adb73b31c3f92a58fcf79d4643364c9",
}

SCENE_HASHES = {
    "calendar": "d58d35aba1b19198466ee4f2b539a3272c5f257226cb06c1d3b6db3f4d041f5f",
    "countdown": "da9ca6e51a69c32c6ac6bc7fa54042355f78623ebe2f9085302efcf1dbc84344",
    "focus": "e585eae3eca7e03f15997ab084b3a0c695632a5fa1fa69ce58e269e56458e0e9",
    "goals": "b97c0a18f347c9b84ca95dda7c19c4cf99c4e0f4e9d0c00be9b6b68ef2fe1532",
    "joy": "d1aa0e12e3d3a9a19d122380bf1defde9c2489a564e88184607444adc82708f2",
    "review": "130d0ba2c13334c135ec5ad1607e39c65af5632e5f29a88256f8287ac6bd717f",
    "settings": "62b1038fb4e034d0f6b41cccc94b9c8c1809e7c3af6feae48509a571c27b383e",
    "smart": "7d71438aaa48e6bc75b24ebf4e58a76361d7d5c67ebf422e6aca326c810140e5",
    "stats": "5fbdfaeb32b59c23faa9373b863835b0172d625121d1a2d2cac85298fa752c02",
    "today": "6d9d2af031e46ac57f768c3c98af1b1db82fcc6112e7e4bc8abd2e69bf53d51b",
    "widgets": "65e6000ab1098fcb76636f54df598e37b3a235766e1ba28b710578df2e770412",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def require_hash(root: Path, rel: str, expected: str) -> dict[str, object]:
    path = root / rel
    if not path.is_file():
        raise FileNotFoundError(f"required source file missing: {rel}")
    actual = sha256(path)
    if actual != expected:
        raise RuntimeError(f"source integrity mismatch for {rel}: {actual} != {expected}")
    return {"path": rel, "size": path.stat().st_size, "sha256": actual}


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"expected exactly one {label} marker, found {count}")
    return text.replace(old, new, 1)


def write_tone(path: Path, notes: list[tuple[float, float, float]]) -> None:
    rate = 22050
    frames: list[int] = []
    for freq, duration, volume in notes:
        sample_count = int(rate * duration)
        for index in range(sample_count):
            attack = min(1.0, index / max(1.0, rate * 0.015))
            release = max(0.0, 1.0 - index / max(1.0, sample_count))
            sample = int(32767 * volume * attack * release * math.sin(2 * math.pi * freq * index / rate))
            frames.append(max(-32768, min(32767, sample)))
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(rate)
        wav.writeframes(b"".join(struct.pack("<h", value) for value in frames))


def main() -> int:
    parser = argparse.ArgumentParser(description="Repair and certify the salvaged PlanJoy R7.3 desktop source tree")
    parser.add_argument("desktop", type=Path)
    parser.add_argument("preload", type=Path)
    args = parser.parse_args()

    root = args.desktop.resolve()
    preload_source = args.preload.resolve()
    if not root.is_dir():
        raise NotADirectoryError(root)
    if not preload_source.is_file():
        raise FileNotFoundError(preload_source)

    verified: list[dict[str, object]] = []
    for rel, digest in EXPECTED.items():
        verified.append(require_hash(root, rel, digest))
    for scene, digest in SCENE_HASHES.items():
        verified.append(require_hash(root, f"assets/scenes/{scene}.svg", digest))

    shutil.copyfile(preload_source, root / "preload.js")

    package_path = root / "package.json"
    package = json.loads(package_path.read_text(encoding="utf-8"))
    build_files = package.setdefault("build", {}).setdefault("files", [])
    if "SOURCE_RECOVERY_MANIFEST.json" not in build_files:
        build_files.append("SOURCE_RECOVERY_MANIFEST.json")
    package_path.write_text(json.dumps(package, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")

    css_path = root / "renderer/app.css"
    css = css_path.read_text(encoding="utf-8")
    css = replace_once(
        css,
        "@font-face{font-family:'IRANSansXV';src:url('../assets/fonts/IRANSansXVF.ttf') format('truetype');font-weight:100 900;font-display:swap}\n",
        "",
        "private font-face",
    )
    css = replace_once(
        css,
        "body.fa{font-family:'IRANSansXV',Tahoma,sans-serif}",
        'body.fa{font-family:Tahoma,"Segoe UI",sans-serif}',
        "Persian font stack",
    )
    css_path.write_text(css, encoding="utf-8", newline="\n")

    app_path = root / "renderer/app.js"
    renderer = app_path.read_text(encoding="utf-8")
    renderer = replace_once(
        renderer,
        "English uses Segoe UI. Persian switches immediately to the embedded IRANSansXV font and full RTL.",
        "English uses Segoe UI. Persian switches immediately to the native Windows font stack and full RTL.",
        "English font description",
    )
    renderer = replace_once(
        renderer,
        "انگلیسی از Segoe UI استفاده می‌کند؛ فارسی بلافاصله به IRANSansXV داخلی و راست‌به‌چپ کامل تغییر می‌کند.",
        "انگلیسی از Segoe UI استفاده می‌کند؛ فارسی بلافاصله از قلم‌های استاندارد ویندوز و راست‌به‌چپ کامل استفاده می‌کند.",
        "Persian font description",
    )
    app_path.write_text(renderer, encoding="utf-8", newline="\n")

    contract_path = root / "tests/desktop_contract_test.js"
    contract = contract_path.read_text(encoding="utf-8")
    contract = replace_once(
        contract,
        "const fs=require('fs'); const path=require('path'); const crypto=require('crypto');",
        "const fs=require('fs'); const path=require('path');",
        "contract crypto import",
    )
    contract = replace_once(contract, "'IRANSansXV'", "'native Windows font stack'", "UI font marker")
    contract = replace_once(
        contract,
        "ok(css.includes('@font-face'),'font face');",
        "ok(css.includes('font-family:Tahoma,\"Segoe UI\",sans-serif'),'system font stack');",
        "font-face contract",
    )
    contract = replace_once(
        contract,
        "const font=fs.readFileSync(path.join(root,'assets/fonts/IRANSansXVF.ttf'));ok(crypto.createHash('sha256').update(font).digest('hex')==='032d3ab20158ce7213e9018197c150000270d96a83e84db68911d71bdbe47240','user IRANSans exact');",
        "ok(!fs.existsSync(path.join(root,'assets/fonts/IRANSansXVF.ttf')),'no private font redistributed');",
        "private font hash contract",
    )
    contract_path.write_text(contract, encoding="utf-8", newline="\n")

    installer_path = root / "installer/main.go"
    installer = installer_path.read_text(encoding="utf-8")
    installer = replace_once(installer, '    "archive/zip"\n', '    "archive/zip"\n    "bytes"\n', "Go bytes import")
    installer = replace_once(
        installer,
        "zip.NewReader(strings.NewReader(string(raw)),int64(len(raw)))",
        "zip.NewReader(bytes.NewReader(raw),int64(len(raw)))",
        "binary ZIP reader",
    )
    installer = replace_once(
        installer,
        'if desktop:=filepath.Join(os.Getenv("USERPROFILE"),"Desktop");os.Getenv("USERPROFILE")!=""{_ = shortcut(filepath.Join(desktop,"PlanJoy.lnk"),appPath,dir,appPath)}',
        'if desktop:=filepath.Join(os.Getenv("USERPROFILE"),"Desktop");os.Getenv("USERPROFILE")!=""{_ = os.MkdirAll(desktop,0755);_ = shortcut(filepath.Join(desktop,"PlanJoy.lnk"),appPath,dir,appPath)}',
        "Desktop shortcut directory",
    )
    installer_path.write_text(installer, encoding="utf-8", newline="\n")

    private_font = root / "assets/fonts/IRANSansXVF.ttf"
    if private_font.exists():
        private_font.unlink()
    fonts_dir = root / "assets/fonts"
    fonts_dir.mkdir(parents=True, exist_ok=True)
    for obsolete_note in ("CI_FONT_NOTE.txt", "README_PRIVATE_FONT.txt"):
        note = fonts_dir / obsolete_note
        if note.exists():
            note.unlink()
    (fonts_dir / "SYSTEM_FONT_POLICY.txt").write_text(
        "PlanJoy R7.3 does not redistribute private font binaries.\n"
        "English uses Segoe UI; Persian uses Tahoma/Segoe UI system fallbacks.\n",
        encoding="utf-8",
        newline="\n",
    )

    sounds = {
        "soft_pop.wav": [(520, 0.12, 0.20), (660, 0.12, 0.14)],
        "focus_start.wav": [(392, 0.18, 0.13), (523, 0.22, 0.12)],
        "reward_chime.wav": [(523, 0.14, 0.14), (659, 0.16, 0.14), (784, 0.28, 0.13)],
    }
    for name, notes in sounds.items():
        write_tone(root / "assets/sounds" / name, notes)

    ico = root / "assets/icons/planjoy.ico"
    if ico.exists():
        ico.unlink()

    post_files = [
        "package.json", "main.js", "preload.js", "renderer/app.js", "renderer/app.css",
        "renderer/index.html", "tests/desktop_contract_test.js", "installer/main.go",
        "assets/icons/planjoy.png", "assets/fonts/SYSTEM_FONT_POLICY.txt",
        "assets/sounds/soft_pop.wav", "assets/sounds/focus_start.wav", "assets/sounds/reward_chime.wav",
    ] + [f"assets/scenes/{name}.svg" for name in sorted(SCENE_HASHES)]

    manifest = {
        "format": "PlanJoy-R73-source-recovery-manifest-v1",
        "version": "0.7.3",
        "archive": {
            "historical_v3_decoded_size": 150092,
            "historical_v3_decoded_sha256": "3edf0aa68f9f7d4731e13dd8d83a4fd00cfe9f766b76f20592f45cb7b9e5837c",
            "note": "The historical XZ stream has a damaged tail; every critical source file is individually hash-verified before repair.",
        },
        "pre_repair_verified_files": verified,
        "post_repair_files": [
            {"path": rel, "size": (root / rel).stat().st_size, "sha256": sha256(root / rel)}
            for rel in post_files
        ],
        "security": {
            "context_isolation": True,
            "node_integration": False,
            "sandbox": True,
            "preload_allowlist": True,
            "private_font_binaries_redistributed": False,
            "installer_scope": "current-user",
        },
    }
    (root / "SOURCE_RECOVERY_MANIFEST.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({"ok": True, "verified": len(verified), "post_files": len(post_files)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
