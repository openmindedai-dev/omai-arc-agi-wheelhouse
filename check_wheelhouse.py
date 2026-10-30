from pathlib import Path
from packaging.requirements import Requirement
from packaging.utils import parse_wheel_filename
from packaging.version import Version

lock = Path("requirements.lock").read_text()
wheel_dir = Path("wheels")

available = {}
for path in wheel_dir.glob("*.whl"):
    name, version, build, tags = parse_wheel_filename(path.name)
    available.setdefault(name, set()).add(version)

missing = []
for line in lock.splitlines():
    line = line.strip()
    if not line or line.startswith("#") or line.startswith("--"):
        continue
    if line.endswith("\\"):
        line = line[:-1].strip()
    if line.startswith("--hash="):
        continue

    try:
        req = Requirement(line)
        if req.marker and not req.marker.evaluate({"python_version": "3.12", "sys_platform": "linux", "platform_machine": "x86_64"}):
            continue
        name = req.name.lower().replace("_", "-")
        versions = available.get(name, set())
        if not any(v in req.specifier for v in versions):
            missing.append(str(req))
    except Exception:
        pass

print("Wheels found:", sum(1 for _ in wheel_dir.glob("*.whl")))
print("Missing requirements:", len(missing))
for item in missing:
    print("MISSING:", item)
