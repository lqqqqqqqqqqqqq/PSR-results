"""Verify frozen result assets, not model outputs. Standard library only."""
from pathlib import Path
import ast
import csv
import hashlib
import json
import struct
import zipfile

ROOT = Path(__file__).resolve().parent

def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def main():
    manifest = json.loads((ROOT / 'MANIFEST.json').read_text(encoding='utf-8'))
    csv_rows = {}
    arrays = {}
    for record in manifest['files']:
        path = (ROOT / record['file']).resolve()
        if not path.is_relative_to(ROOT) or not path.is_file():
            raise RuntimeError('Missing or unsafe asset: ' + record['file'])
        if path.stat().st_size != record['bytes'] or digest(path) != record['sha256']:
            raise RuntimeError('Hash or size mismatch: ' + record['file'])
        if path.suffix.lower() == '.csv':
            with path.open(encoding='utf-8-sig', newline='') as stream:
                reader = csv.DictReader(stream)
                if not reader.fieldnames:
                    raise RuntimeError('Missing CSV header')
                csv_rows[record['file']] = sum(1 for _ in reader)
        if path.suffix.lower() == '.npz':
            with zipfile.ZipFile(path) as archive:
                if archive.testzip() is not None:
                    raise RuntimeError('Corrupt NPZ')
                for member in archive.namelist():
                    with archive.open(member) as stream:
                        if stream.read(6) != b'\x93NUMPY':
                            raise RuntimeError('Not a NumPy array')
                        version = stream.read(2)
                        size = struct.unpack('<H' if version[0] == 1 else '<I', stream.read(2 if version[0] == 1 else 4))[0]
                        header = ast.literal_eval(stream.read(size).decode('latin1').strip())
                        descriptor = header['descr']
                        if not isinstance(descriptor, str) or not any(c in descriptor for c in 'biufc') or any(c in descriptor for c in 'OSUV'):
                            raise RuntimeError('Non-numeric NPZ dtype: ' + str(descriptor))
                        arrays[member] = {'shape': list(header['shape']), 'dtype': descriptor}
    print(json.dumps({'status': 'PASS', 'verified_files': len(manifest['files']), 'csv_row_counts': csv_rows, 'numeric_arrays': arrays, 'model_code_executed': False, 'network': False}, indent=2))

if __name__ == '__main__':
    main()
