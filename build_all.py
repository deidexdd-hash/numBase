#!/usr/bin/env python3
"""
ГЛАВНЫЙ ЗАПУСКАТЕЛЬ ГИБРИДНОЙ СИСТЕМЫ
Выполняет все этапы создания базы знаний.
"""

import sys
import subprocess
from pathlib import Path

print("=" * 80)
print("  ГИБРИДНАЯ СИСТЕМА БАЗЫ ЗНАНИЙ")
print("  Ансестология и Нумерология")
print("=" * 80)
print()

processor_dir = Path(__file__).parent

def run_stage(name, script):
    """Запустить этап обработки"""
    print(f"\n{'='*80}")
    print(f"  ЭТАП: {name}")
    print("=" * 80)
    
    script_path = processor_dir / script
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=processor_dir.parent,
            capture_output=False
        )
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

# Этап 1: Создание JSON базы (лёгкие формулы)
print("\n▶ Запускаю создание лёгкой JSON базы...")
if not run_stage("Создание JSON базы (формулы)", "processor/create_database.py"):
    print("❌ Остановка")
    sys.exit(1)

# Этап 2: Создание SQLite базы (полный текст)
print("\n▶ Запускаю создание полнотекстовой SQLite базы...")
print("  ⚠ Это займет время (83 PDF файла, ~210 MB)")
print()

if not run_stage("Извлечение текста из PDF", "processor/build_full_database.py"):
    print("❌ Остановка")
    sys.exit(1)

print("\n" + "=" * 80)
print("  ✅ ВСЕ ЭТАПЫ ЗАВЕРШЕНЫ!")
print("=" * 80)
print()
print("Создано:")
print("  📁 data/formulas.json        - 15 формул расчетов")
print("  📁 data/practices.json       - 8 практик")
print("  📁 data/number_meanings.json - 11 значений чисел")
print("  📁 data/algorithms.json      - 2 алгоритма")
print("  🗄️  data/knowledge_base.db    - полный текст 83 PDF")
print("  📄 data/master_index.json    - общий индекс")
print()
print("Использование:")
print("  from knowledge_base import HybridKnowledgeBase")
print("  kb = HybridKnowledgeBase()")
print("  ")
print("  # Расчеты (мгновенно из JSON)")
print("  result = kb.calculate_life_path(15, 6, 1990)")
print("  ")
print("  # Поиск (полнотекстовый по SQLite)")
print("  docs = kb.search_documents('финансовый канал')")
print()
print("=" * 80)
