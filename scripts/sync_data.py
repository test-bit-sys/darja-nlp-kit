"""Sync linguistic datasets from /data to both JS and Python packages."""
import json
import shutil
import sys
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    data_dir = root / 'data'

    targets = [
        root / 'packages' / 'js' / 'data',
        root / 'packages' / 'python' / 'darja_nlp' / 'data',
    ]

    data_files = [
        'stopwords.json',
        'lexicon.json',
        'arabizi_rules.json',
        'wilayas.json',
        'dialects.json',
        'dialogues.json'
    ]

    for src_name in data_files:
        src_path = data_dir / src_name
        if not src_path.exists():
            print(f'[ERROR] Source file not found: {src_path}', file=sys.stderr)
            sys.exit(1)

    for target_dir in targets:
        target_dir.mkdir(parents=True, exist_ok=True)
        print(f'[SYNC] Target directory: {target_dir}')

        for src_name in data_files:
            src_path = data_dir / src_name
            dst_path = target_dir / src_name

            with open(src_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            with open(dst_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            print(f'  [OK] {src_name} -> {dst_path.relative_to(root)}')

    print('\n[DONE] All datasets synced successfully.')

    root_readme = root / 'README.md'
    if root_readme.exists():
        for pkg in ['js', 'python']:
            pkg_readme = root / 'packages' / pkg / 'README.md'
            shutil.copyfile(root_readme, pkg_readme)
            print(f'  [OK] README.md -> {pkg_readme.relative_to(root)}')

    for target_dir in targets:
        total_entries = 0
        for src_name in data_files:
            file_path = target_dir / src_name
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if src_name == 'stopwords.json':
                count = sum(len(v) for v in data.values())
                total_entries += count
                print(f'  [STATS] {src_name}: {count} stopwords across {len(data)} categories')
            elif src_name == 'lexicon.json':
                pos = len(data.get('positive', {}))
                neg = len(data.get('negative', {}))
                negators = len(data.get('negators', []))
                intensifiers = len(data.get('intensifiers', {}))
                total_entries += pos + neg
                print(f'  [STATS] {src_name}: {pos} positive, {neg} negative, '
                      f'{negators} negators, {intensifiers} intensifiers')
            elif src_name == 'arabizi_rules.json':
                overrides = len(data.get('overrides', {}))
                french = len(data.get('french_whitelist', []))
                print(f'  [STATS] {src_name}: {overrides} overrides, {french} French whitelist entries')
            elif src_name == 'wilayas.json':
                print(f'  [STATS] {src_name}: {len(data)} wilayas registered')


if __name__ == '__main__':
    main()
