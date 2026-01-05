#!/usr/bin/env python3
"""Verify and complete FreDeSa repository cleanup."""

import os
import shutil
from pathlib import Path

def main():
    root = Path("/Users/delchaplin/Project Files/fredesa-ai-platform")
    os.chdir(root)
    
    print("🔍 FreDeSa Repository Cleanup Verification\n")
    
    # Check current root files
    root_files = [f for f in os.listdir(root) if os.path.isfile(f)]
    print(f"📁 Current root files: {len(root_files)}")
    for f in sorted(root_files):
        if not f.startswith('.'):
            print(f"   - {f}")
    
    print("\n🔧 Performing cleanup operations...\n")
    
    # 1. Remove .DS_Store if exists
    ds_store = root / ".DS_Store"
    if ds_store.exists():
        ds_store.unlink()
        print("✅ Removed .DS_Store")
    else:
        print("✅ .DS_Store already removed")
    
    # 2. Move .env.production to config/env/
    env_prod_src = root / ".env.production"
    env_prod_dst = root / "config" / "env" / "production.env"
    if env_prod_src.exists():
        env_prod_dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(env_prod_src), str(env_prod_dst))
        print(f"✅ Moved .env.production → config/env/production.env")
    else:
        print("✅ .env.production already moved")
    
    # 3. Move .env.test to config/env/
    env_test_src = root / ".env.test"
    env_test_dst = root / "config" / "env" / "test.env"
    if env_test_src.exists():
        env_test_dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(env_test_src), str(env_test_dst))
        print(f"✅ Moved .env.test → config/env/test.env")
    else:
        print("✅ .env.test already moved")
    
    # 4. Archive reorganize.sh
    reorg_src = root / "reorganize.sh"
    reorg_dst = root / "archive" / "scripts" / "reorganize.sh"
    if reorg_src.exists():
        reorg_dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(reorg_src), str(reorg_dst))
        print(f"✅ Archived reorganize.sh → archive/scripts/")
    else:
        print("✅ reorganize.sh already archived")
    
    # Final verification
    print("\n📊 Final State:")
    root_files = [f for f in os.listdir(root) if os.path.isfile(f) and not f.startswith('.')]
    print(f"   Root files (non-hidden): {len(root_files)}")
    for f in sorted(root_files):
        print(f"   - {f}")
    
    # Check target is 4 files: README.md, NEXT_SESSION_START_HERE.md, REPOSITORY_STRUCTURE.md, docker-compose.yml
    target_files = ["README.md", "NEXT_SESSION_START_HERE.md", "REPOSITORY_STRUCTURE.md", "docker-compose.yml"]
    if set(root_files) == set(target_files):
        print("\n✨ SUCCESS! Repository cleanup complete!")
        print(f"   Target achieved: {len(target_files)} root files")
    else:
        print(f"\n⚠️  Close! Expected {len(target_files)} files, have {len(root_files)}")
        extra = set(root_files) - set(target_files)
        if extra:
            print(f"   Extra files: {extra}")

if __name__ == "__main__":
    main()
