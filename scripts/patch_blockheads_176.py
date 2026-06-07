import argparse
import hashlib
import json
import sys
import tempfile
import zipfile
from pathlib import Path


EXPECTED_APK_SHA256 = "29bd526000c04f24ba10b16da9c6c9a57181e40d9bef48c29526aed29c3371eb"
EXPECTED_LIB_SHA256 = "7701c409a115886e0fed1cab508995796b144136cfb3d5dafd37ffe002e0e412"
TARGET_ENTRY = "lib/armeabi-v7a/libCoreText.so"
PATCHED_APK_SHA256 = "229e5dec00c64de760546bc734ede7a1fa92ec23d1df5ec3d540f9a94ac06219"

V1_CHECKS = {
    0xC408: bytes.fromhex("fcceffff"),
    0xC31C: bytes.fromhex("14001be5"),
    0xC320: bytes.fromhex("3bf8ffeb"),
    0xC324: bytes.fromhex("18000be5"),
}

V2_CHECKS = {
    0xCF88: bytes.fromhex("00482de9"),
    0xCF8C: bytes.fromhex("0db0a0e1"),
    0xCF90: bytes.fromhex("08d04de2"),
    0xCF94: bytes.fromhex("04008de5"),
    0xCF98: bytes.fromhex("04009de5"),
    0xCF9C: bytes.fromhex("0c0090e5"),
    0xCFA0: bytes.fromhex("45f5ffeb"),
    0xCFA4: bytes.fromhex("0bd0a0e1"),
    0xCFA8: bytes.fromhex("0088bde8"),
}

V2_PATCH = bytes.fromhex(
    "00482de90db0a0e1000050e30200000a0c0090e5000050e345f5ff1b0bd0a0e10088bde8"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_bytes(blob: bytes, checks: dict[int, bytes], label: str) -> None:
    for offset, expected in checks.items():
        actual = blob[offset : offset + len(expected)]
        if actual != expected:
            raise ValueError(
                f"{label} precheck failed at {offset:#x}: "
                f"got {actual.hex()} expected {expected.hex()}"
            )


def apply_patches(blob: bytearray) -> None:
    verify_bytes(blob, V1_CHECKS, "v1")
    blob[0xC408:0xC40C] = bytes.fromhex("bcceffff")
    blob[0xC31C:0xC320] = bytes.fromhex("000050e3")
    blob[0xC320:0xC324] = bytes.fromhex("3600000a")
    blob[0xC324:0xC328] = bytes.fromhex("3af8ffeb")
    blob[0xC328:0xC32C] = bytes.fromhex("18000be5")

    verify_bytes(blob, V2_CHECKS, "v2")
    blob[0xCF88 : 0xCF88 + len(V2_PATCH)] = V2_PATCH


def patch_apk(input_apk: Path, output_apk: Path) -> dict[str, str]:
    if sha256_file(input_apk) != EXPECTED_APK_SHA256:
        raise ValueError("Input APK SHA256 does not match the expected original build")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_root = Path(temp_dir)
        extracted_lib = temp_root / "libCoreText.so"

        with zipfile.ZipFile(input_apk, "r") as source_zip:
            extracted_lib.write_bytes(source_zip.read(TARGET_ENTRY))

        original_lib_sha = sha256_file(extracted_lib)
        if original_lib_sha != EXPECTED_LIB_SHA256:
            raise ValueError("Input libCoreText.so SHA256 does not match expected value")

        data = bytearray(extracted_lib.read_bytes())
        apply_patches(data)
        extracted_lib.write_bytes(data)
        patched_lib_sha = sha256_file(extracted_lib)

        with zipfile.ZipFile(input_apk, "r") as source_zip, zipfile.ZipFile(
            output_apk, "w"
        ) as target_zip:
            for info in source_zip.infolist():
                upper_name = info.filename.upper()
                if upper_name.startswith("META-INF/") and upper_name.endswith(
                    (".MF", ".SF", ".RSA", ".DSA")
                ):
                    continue
                if info.filename == TARGET_ENTRY:
                    target_zip.writestr(info, extracted_lib.read_bytes())
                else:
                    target_zip.writestr(info, source_zip.read(info.filename))

    output_sha = sha256_file(output_apk)
    return {
        "input_apk_sha256": EXPECTED_APK_SHA256,
        "input_lib_sha256": EXPECTED_LIB_SHA256,
        "patched_lib_sha256": patched_lib_sha,
        "output_apk_sha256": output_sha,
        "reference_patched_apk_sha256": PATCHED_APK_SHA256,
        "output_matches_reference_apk": output_sha == PATCHED_APK_SHA256,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Patch The Blockheads 1.7.6 for modern Android compatibility"
    )
    parser.add_argument("--input", required=True, help="Path to the original APK")
    parser.add_argument(
        "--output", required=True, help="Path for the patched unsigned APK"
    )
    parser.add_argument(
        "--print-json", action="store_true", help="Print result metadata as JSON"
    )
    args = parser.parse_args()

    input_apk = Path(args.input)
    output_apk = Path(args.output)
    output_apk.parent.mkdir(parents=True, exist_ok=True)

    try:
        metadata = patch_apk(input_apk, output_apk)
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.print_json:
        print(json.dumps(metadata, indent=2, sort_keys=True))
    else:
        print(f"patched apk written to: {output_apk}")
        print(f"patched lib sha256: {metadata['patched_lib_sha256']}")
        print(f"output apk sha256: {metadata['output_apk_sha256']}")
        if metadata["output_apk_sha256"] != metadata["reference_patched_apk_sha256"]:
            print(
                "note: output apk sha256 differs from the repository reference; "
                "this can happen when zip metadata or packaging details differ"
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
