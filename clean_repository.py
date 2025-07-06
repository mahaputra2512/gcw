#!/usr/bin/env python3
"""
Script untuk membersihkan repository dari file-file sensitif
sebelum commit ke GitHub
"""

import os
import shutil
import glob

def clean_repository():
    """Bersihkan file-file sensitif dari repository"""
    
    print("🧹 Membersihkan repository dari file-file sensitif...")
    
    # File dan direktori yang akan dihapus
    files_to_remove = [
        "hoax_detector.db",
        "*.db",
        ".env",
        ".env.local",
        ".env.development.local",
        ".env.test.local",
        ".env.production.local",
    ]
    
    directories_to_remove = [
        "logs",
        "reports", 
        "visualizations",
        "__pycache__",
        "*.pyc",
        ".pytest_cache",
        ".mypy_cache",
    ]
    
    removed_files = []
    
    # Hapus file
    for pattern in files_to_remove:
        for file_path in glob.glob(pattern):
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    removed_files.append(file_path)
                    print(f"✅ Removed: {file_path}")
            except Exception as e:
                print(f"❌ Error removing {file_path}: {e}")
    
    # Hapus direktori
    for pattern in directories_to_remove:
        for dir_path in glob.glob(pattern):
            try:
                if os.path.exists(dir_path) and os.path.isdir(dir_path):
                    shutil.rmtree(dir_path)
                    removed_files.append(dir_path)
                    print(f"✅ Removed directory: {dir_path}")
            except Exception as e:
                print(f"❌ Error removing directory {dir_path}: {e}")
    
    # Hapus file __pycache__ di dalam direktori
    for root, dirs, files in os.walk("."):
        if "__pycache__" in dirs:
            pycache_path = os.path.join(root, "__pycache__")
            try:
                shutil.rmtree(pycache_path)
                removed_files.append(pycache_path)
                print(f"✅ Removed: {pycache_path}")
            except Exception as e:
                print(f"❌ Error removing {pycache_path}: {e}")
    
    # Hapus file .pyc
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".pyc"):
                pyc_path = os.path.join(root, file)
                try:
                    os.remove(pyc_path)
                    removed_files.append(pyc_path)
                    print(f"✅ Removed: {pyc_path}")
                except Exception as e:
                    print(f"❌ Error removing {pyc_path}: {e}")
    
    print(f"\n🎉 Pembersihan selesai! {len(removed_files)} file/direktori dihapus.")
    
    # Tampilkan pesan
    print("\n📋 Langkah selanjutnya:")
    print("1. Pastikan file .gitignore sudah dibuat")
    print("2. Salin env.example ke .env dan isi dengan kredensial Anda")
    print("3. Baca SECURITY.md untuk panduan setup")
    print("4. Commit perubahan ke GitHub")
    print("\n⚠️  PERINGATAN: Pastikan tidak ada kredensial yang tersisa di kode!")

if __name__ == "__main__":
    clean_repository() 