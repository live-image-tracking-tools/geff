import argparse

from geff.metadata_schema import write_metadata_schema

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--filename", default="geff-schema.json")
    args = parser.parse_args()

    write_metadata_schema(args.filename)
