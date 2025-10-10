#!/usr/bin/env python3
"""
현재 결과를 Google Drive에 백업하는 유틸리티
실행 중인 벤치마크 결과를 안전하게 백업합니다.
"""

import os
import glob
import shutil
import json
from pathlib import Path

def backup_results_to_gdrive():
    """현재 디렉토리의 결과를 Google Drive에 백업"""

    # Google Drive 디렉토리 확인
    gdrive_dir = os.environ.get('GDRIVE_RESULTS_DIR')

    if not gdrive_dir:
        print("❌ GDRIVE_RESULTS_DIR 환경 변수가 설정되지 않았습니다.")
        print("   Colab에서 다음을 실행하세요:")
        print("   os.environ['GDRIVE_RESULTS_DIR'] = '/content/drive/MyDrive/AI_Benchmark_Results'")
        return False

    if not os.path.exists(gdrive_dir):
        print(f"❌ Google Drive 디렉토리가 없습니다: {gdrive_dir}")
        print("   Google Drive를 마운트했는지 확인하세요.")
        return False

    # 현재 디렉토리의 결과 파일 찾기
    result_files = []

    # JSON 결과 파일
    result_files.extend(glob.glob("benchmark_results_*.json"))
    result_files.extend(glob.glob("results/benchmark_results_*.json"))

    # CSV 결과 파일
    result_files.extend(glob.glob("benchmark_results_*.csv"))
    result_files.extend(glob.glob("results/benchmark_results_*.csv"))

    if not result_files:
        print("⚠️  백업할 결과 파일이 없습니다.")
        return False

    # 파일 백업
    backup_count = 0
    for file_path in result_files:
        try:
            filename = os.path.basename(file_path)
            dest_path = os.path.join(gdrive_dir, filename)

            shutil.copy2(file_path, dest_path)
            backup_count += 1
            print(f"✅ 백업 완료: {filename}")

        except Exception as e:
            print(f"❌ 백업 실패 ({filename}): {e}")

    print(f"\n💾 총 {backup_count}개 파일 백업 완료!")
    print(f"📁 저장 위치: {gdrive_dir}")

    return True

def list_gdrive_backups():
    """Google Drive의 백업 목록 표시"""
    gdrive_dir = os.environ.get('GDRIVE_RESULTS_DIR')

    if not gdrive_dir or not os.path.exists(gdrive_dir):
        print("❌ Google Drive 디렉토리를 찾을 수 없습니다.")
        return

    # 결과 파일 찾기
    json_files = glob.glob(os.path.join(gdrive_dir, "benchmark_results_*.json"))
    csv_files = glob.glob(os.path.join(gdrive_dir, "benchmark_results_*.csv"))
    backup_files = glob.glob(os.path.join(gdrive_dir, "backup_progress_*.json"))

    print(f"\n📁 Google Drive 백업 목록: {gdrive_dir}")
    print("=" * 60)

    if json_files:
        print(f"\n📊 결과 파일 (JSON): {len(json_files)}개")
        for f in sorted(json_files, key=os.path.getctime, reverse=True)[:5]:
            size = os.path.getsize(f) / 1024  # KB
            print(f"   - {os.path.basename(f)} ({size:.1f} KB)")

    if csv_files:
        print(f"\n📈 결과 파일 (CSV): {len(csv_files)}개")
        for f in sorted(csv_files, key=os.path.getctime, reverse=True)[:5]:
            size = os.path.getsize(f) / 1024  # KB
            print(f"   - {os.path.basename(f)} ({size:.1f} KB)")

    if backup_files:
        print(f"\n💾 중간 백업 파일: {len(backup_files)}개")
        for f in sorted(backup_files, key=os.path.getctime, reverse=True)[:3]:
            size = os.path.getsize(f) / 1024  # KB

            # 진행 상황 읽기
            try:
                with open(f, 'r') as file:
                    data = json.load(file)
                    progress = data.get('progress', 'N/A')
                    print(f"   - {os.path.basename(f)} - 진행: {progress} ({size:.1f} KB)")
            except:
                print(f"   - {os.path.basename(f)} ({size:.1f} KB)")

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "list":
        list_gdrive_backups()
    else:
        backup_results_to_gdrive()
