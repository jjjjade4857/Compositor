#!/usr/bin/env python3
"""Build the local Chinese edition using Apple's installed command-line tools."""
from pathlib import Path
import concurrent.futures
import subprocess
import os

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "build/zh-Hans"
BUILD.mkdir(parents=True, exist_ok=True)
(BUILD / "localization").mkdir(exist_ok=True)
SDK = "/Library/Developer/CommandLineTools/SDKs/MacOSX26.5.sdk"
if not Path(SDK).is_dir():
    SDK = subprocess.check_output(["xcrun", "--show-sdk-path"], text=True).strip()

def compile_c(source):
    obj = BUILD / (source.stem + ".o")
    subprocess.run(["xcrun", "clang", "-c", "-O3", "-fblocks", "-target", "arm64-apple-macos26.0", "-isysroot", SDK, str(source), "-o", str(obj)], check=True)
    return str(obj)

with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    objects = list(pool.map(compile_c, sorted((ROOT / "Compositor").rglob("*.c"))))
sources = [str(p) for p in sorted((ROOT / "Compositor").rglob("*.swift")) if p.name != "UpdateDriver.swift"]
command = ["xcrun", "swiftc", "-O", "-whole-module-optimization", "-num-threads", "6", "-parse-as-library", "-module-name", "Compositor", "-swift-version", "5", "-default-isolation", "MainActor", "-target", "arm64-apple-macos26.0", "-sdk", SDK, "-import-objc-header", str(ROOT / "Compositor/Compositor-Bridging-Header.h"), "-emit-localized-strings", "-emit-localized-strings-path", str(BUILD / "localization")]
for feature in ["NonisolatedNonsendingByDefault", "InferIsolatedConformances", "InferSendableFromCaptures", "DisableOutwardActorInference", "GlobalActorIsolatedTypesUsability", "MemberImportVisibility"]:
    command += ["-enable-upcoming-feature", feature]
command += sources + objects + ["-o", str(BUILD / "Compositor")]
print(f"Building {len(sources)} Swift sources and {len(objects)} C objects", flush=True)
result = subprocess.run(command, cwd=ROOT)
if result.returncode:
    raise SystemExit(result.returncode)
print("Build complete", flush=True)
