# script to convert json to yaml
"""
JSON to YAML Conversion Utility.

Contracts and Dependency Specifications:
- Pure conversion:
    json_to_yaml(data, sort_keys=False) -> str
    Dependencies: None (pure computation; no disk, network, clock, or UI state).
    Guarantees: Bit-for-bit repeatability across repeated and interleaved executions;
                zero input mutation.
- File-based conversion:
    convert_json_to_yaml(source_path, target_path=None) -> str
    Dependencies: Filesystem read (source_path) and optional write (target_path).
    Seam: Accepts explicit source and target paths with defaults preserving callers.
- CLI Entrypoint:
    main(argv=None) -> int
    CLI interface parsing sys.argv or injected argv vector.
"""
import json
import os
import sys
import yaml


def json_to_yaml(data, sort_keys: bool = False) -> str:
    """
    Pure conversion of in-memory JSON data structure to YAML formatted string.

    Contract:
    - Precondition: data is a valid JSON-serializable Python structure (dict, list, primitive).
    - Dependencies: None.
    - Idempotency & Repeatability: Repeated executions on equivalent inputs return identical strings.
    - Input Immutability: data is not modified in-place.
    """
    return yaml.dump(data, sort_keys=sort_keys)


def convert_json_to_yaml(source_path: str, target_path: str = None, sort_keys: bool = False) -> str:
    """
    Convert a JSON file to YAML. If target_path is specified, writes to file;
    otherwise returns the YAML string.

    Contract:
    - Preconditions: source_path must exist on disk.
    - Dependencies: Filesystem I/O (injected via parameters).
    - If target_path exists: raises FileExistsError (or handled by CLI).
    """
    if not os.path.exists(source_path):
        raise FileNotFoundError(f"ERROR: {source_path} not found")

    with open(source_path, "r", encoding="utf-8") as sourcefile:
        contentsource = json.load(sourcefile)

    outs = json_to_yaml(contentsource, sort_keys=sort_keys)

    if target_path:
        if os.path.exists(target_path):
            raise FileExistsError(f"ERROR: {target_path} already exists")
        with open(target_path, "w", encoding="utf-8") as target_file:
            target_file.write(outs)

    return outs


def main(argv=None):
    if argv is None:
        argv = sys.argv

    if len(argv) > 1:
        if os.path.exists(argv[1]):
            sourcefile = open(argv[1], "r", encoding="utf-8")
            contentsource = json.load(sourcefile)
            sourcefile.close()
        else:
            print("ERROR: " + argv[1] + " not found")
            return 1
    else:
        print("Usage: json2yaml.py <sourcefile.json> [target_file.yaml]")
        return 1

    outs = yaml.dump(contentsource, sort_keys=False)

    if len(argv) < 3:
        print(outs)
    elif os.path.exists(argv[2]):
        print("ERROR: " + argv[2] + " already exists")
        return 1
    else:
        target_file = open(argv[2], "w", encoding="utf-8")
        target_file.write(outs)
        target_file.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
##end
