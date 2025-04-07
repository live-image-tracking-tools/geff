import argparse
import json

from geff.metadata_schema import GeffMetadata

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--filename", default="geff-schema.json")
    args = parser.parse_args()

    with open(args.filename, "w") as f:
        f.write(json.dumps(GeffMetadata.model_json_schema()))
