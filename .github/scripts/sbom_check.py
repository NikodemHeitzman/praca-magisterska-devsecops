"""Check of the sbom job: the SBOM files exist, have the expected schema and are not empty.

The sbom job is fail closed without a severity threshold (ADR-0042, B22; ADR-0049): Syft writes
an SPDX JSON and a CycloneDX JSON document of the image archive built by the build job of devsecops-ci.yml, and this
script checks them before the job passes (ADR-0049, S3):

- both files are readable JSON;
- the schema versions are the expected ones (EXPECTED_SPDX, EXPECTED_CYCLONEDX): a Syft update
  that changes the format stops the job, so the format of the experiment data stays explicit;
- the SBOM describes a container image, has operating system packages (`pkg:deb`) and Python
  packages (`pkg:pypi`), so an empty or partial SBOM does not pass;
- both documents describe the same image (the image digest computed by Syft: SPDX root package
  checksum = CycloneDX metadata component version; the job does not set --source-version, which
  would replace it) and list the same packages (the same set of purls);
- the image label `org.opencontainers.image.revision` is the commit of this run, so the SBOM
  describes the image built from this commit (ADR-0049, S5).

The image config digest from the archive (`manifest.json`) goes to the job summary: it is the
image ID that Trivy reports in the build job (`Metadata.ImageID`), which links the SBOM to the scan.
Only the standard library is used, so the script runs without installing anything.

Usage: python sbom_check.py --spdx sbom/sbom.spdx.json --cyclonedx sbom/sbom.cdx.json \
           --archive image.tar --revision <commit sha>
Exit code: 0 pass, 1 check failed, 2 unusable input.
"""

import argparse
import json
import os
import sys
import tarfile
from collections import Counter

EXPECTED_SPDX = "SPDX-2.3"
EXPECTED_CYCLONEDX = "1.7"
REQUIRED_PURL_TYPES = ("deb", "pypi")
REVISION_PROPERTY = "syft:image:labels:org.opencontainers.image.revision"


class InputError(Exception):
    pass


def load_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        raise InputError(f"{path}: {e}") from e
    if not isinstance(data, dict):
        raise InputError(f"{path}: not a JSON object")
    return data


def config_digest(archive):
    """Image config digest from the docker save archive (manifest.json, single image)."""
    try:
        with tarfile.open(archive) as tar:
            member = tar.extractfile("manifest.json")
            manifest = json.load(member) if member else None
    except (OSError, KeyError, tarfile.TarError, json.JSONDecodeError) as e:
        raise InputError(f"{archive}: {e}") from e
    if not isinstance(manifest, list) or len(manifest) != 1 or "Config" not in manifest[0]:
        raise InputError(f"{archive}: manifest.json does not describe exactly one image")
    return "sha256:" + manifest[0]["Config"].rsplit("/", 1)[-1].removesuffix(".json")


def purl_type(purl):
    return purl.split(":", 1)[1].split("/", 1)[0] if purl.startswith("pkg:") else ""


def spdx_facts(doc):
    root_ids = [
        r.get("relatedSpdxElement")
        for r in doc.get("relationships") or []
        if r.get("spdxElementId") == "SPDXRef-DOCUMENT" and r.get("relationshipType") == "DESCRIBES"
    ]
    packages = doc.get("packages") or []
    root = next((p for p in packages if p.get("SPDXID") in root_ids), {})
    purls = {
        ref.get("referenceLocator")
        for p in packages
        if p is not root
        for ref in p.get("externalRefs") or []
        if ref.get("referenceType") == "purl"
    }
    checksum = next(
        (c.get("checksumValue") for c in root.get("checksums") or [] if c.get("algorithm") == "SHA256"),
        None,
    )
    tool = next((c for c in doc.get("creationInfo", {}).get("creators") or [] if c.startswith("Tool:")), None)
    return {
        "version": doc.get("spdxVersion"),
        "root_purpose": root.get("primaryPackagePurpose"),
        "digest": f"sha256:{checksum}" if checksum else None,
        "purls": purls,
        "packages": len(packages) - (1 if root else 0),
        "files": len(doc.get("files") or []),
        "tool": tool,
    }


def cyclonedx_facts(doc):
    metadata = doc.get("metadata") or {}
    component = metadata.get("component") or {}
    components = doc.get("components") or []
    revision = next(
        (p.get("value") for p in metadata.get("properties") or [] if p.get("name") == REVISION_PROPERTY),
        None,
    )
    return {
        "format": doc.get("bomFormat"),
        "version": doc.get("specVersion"),
        "root_type": component.get("type"),
        "digest": component.get("version"),
        "purls": {c["purl"] for c in components if c.get("purl")},
        "types": Counter(c.get("type") for c in components),
        "revision": revision,
    }


def checks(spdx, cdx, revision):
    """List of (check, passed, detail)."""
    spdx_types = Counter(purl_type(p) for p in spdx["purls"])
    result = [
        ("SPDX version", spdx["version"] == EXPECTED_SPDX, f"{spdx['version']} (expected {EXPECTED_SPDX})"),
        (
            "CycloneDX version",
            cdx["format"] == "CycloneDX" and cdx["version"] == EXPECTED_CYCLONEDX,
            f"{cdx['format']} {cdx['version']} (expected CycloneDX {EXPECTED_CYCLONEDX})",
        ),
        (
            "describes a container image",
            spdx["root_purpose"] == "CONTAINER" and cdx["root_type"] == "container",
            f"SPDX {spdx['root_purpose']}, CycloneDX {cdx['root_type']}",
        ),
    ]
    for t in REQUIRED_PURL_TYPES:
        result.append((f"`pkg:{t}` packages", spdx_types[t] > 0, str(spdx_types[t])))
    result += [
        (
            "same image in both documents",
            bool(spdx["digest"]) and spdx["digest"] == cdx["digest"],
            f"SPDX {spdx['digest']}, CycloneDX {cdx['digest']}",
        ),
        (
            "same packages in both documents",
            spdx["purls"] == cdx["purls"],
            f"{len(spdx['purls'])} purls in SPDX, {len(cdx['purls'])} in CycloneDX, "
            f"{len(spdx['purls'] ^ cdx['purls'])} differ",
        ),
        ("image built from this commit", cdx["revision"] == revision, f"label {cdx['revision']}"),
    ]
    return result, spdx_types


def summary(lines):
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if path:
        with open(path, "a", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--spdx", required=True)
    parser.add_argument("--cyclonedx", required=True)
    parser.add_argument("--archive", required=True)
    parser.add_argument("--revision", required=True)
    args = parser.parse_args()

    try:
        spdx = spdx_facts(load_json(args.spdx))
        cdx = cyclonedx_facts(load_json(args.cyclonedx))
        image_id = config_digest(args.archive)
    except InputError as e:
        print(f"::error::sbom check input unusable: {e}")
        return 2

    result, spdx_types = checks(spdx, cdx, args.revision)
    failed = [name for name, ok, _ in result if not ok]
    for name, ok, detail in result:
        if not ok:
            print(f"::error::sbom check failed: {name}: {detail}")

    summary(
        [
            "### SBOM (Syft)",
            "",
            f"Image config digest `{image_id}` (= Trivy `ImageID` in build), "
            f"manifest digest in the SBOM `{spdx['digest']}`, {spdx['tool']}",
            "",
            "| file | format | packages | files |",
            "|---|---|---|---|",
            f"| `{os.path.basename(args.spdx)}` | {spdx['version']} | {spdx['packages']} | {spdx['files']} |",
            f"| `{os.path.basename(args.cyclonedx)}` | CycloneDX {cdx['version']} | "
            f"{sum(n for t, n in cdx['types'].items() if t != 'file')} | {cdx['types']['file']} |",
            "",
            "Packages by purl type: " + ", ".join(f"{t} {n}" for t, n in sorted(spdx_types.items())),
            "",
            "| check | result | detail |",
            "|---|---|---|",
            *(f"| {name} | {'ok' if ok else '**FAIL**'} | {detail} |" for name, ok, detail in result),
            "",
            f"Result: **{'FAIL' if failed else 'PASS'}**",
        ]
    )
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
