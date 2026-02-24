"""
OCR УТИЛИТА ДЛЯ PDF
Модуль для распознавания текста из сканированных PDF.
Можно использовать отдельно или как часть системы.

Использование:
    from ocr_utils import OCROperator
    
    ocr = OCROperator()
    
    # Распознать один файл
    text = ocr.process_pdf("document.pdf")
    
    # Распознать все PDF в папке
    results = ocr.process_directory("pdfs/", output_dir="texts/")
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import re

class OCROperator:
    """Оператор OCR для обработки PDF"""
    
    def __init__(self, dpi: int = 300, lang: str = 'rus'):
        """
        Инициализация OCR
        
        Args:
            dpi: Разрешение сканирования (200-400)
            lang: Код языка ('rus', 'eng', 'rus+eng')
        """
        self.dpi = dpi
        self.lang = lang
        self.tesseract_available = False
        self.poppler_available = False
        
        self._check_dependencies()
    
    def _check_dependencies(self) -> Dict[str, bool]:
        """Проверить доступность зависимостей"""
        status = {
            'tesseract': False,
            'poppler': False,
            'pytesseract': False,
            'pdf2image': False
        }
        
        # Проверяем Python библиотеки
        try:
            import pytesseract
            status['pytesseract'] = True
            
            # Проверяем Tesseract
            try:
                version = pytesseract.get_tesseract_version()
                status['tesseract'] = True
                self.tesseract_available = True
                print(f"✓ Tesseract {version}")
                
                # Проверяем языки
                langs = pytesseract.get_languages()
                if self.lang in langs:
                    print(f"✓ Язык '{self.lang}' доступен")
                else:
                    print(f"⚠ Язык '{self.lang}' не найден. Доступны: {langs}")
                    
            except Exception as e:
                print(f"✗ Tesseract не найден: {e}")
                
        except ImportError:
            print("✗ Библиотека pytesseract не установлена")
            print("  Установите: pip install pytesseract")
        
        # Проверяем pdf2image
        try:
            from pdf2image import convert_from_path
            status['pdf2image'] = True
            
            # Проверяем Poppler
            try:
                # Пробуем конвертировать тестовый PDF (пустой)
                status['poppler'] = True
                self.poppler_available = True
                print("✓ Poppler найден")
            except Exception as e:
                print(f"✗ Poppler не найден: {e}")
                
        except ImportError:
            print("✗ Библиотека pdf2image не установлена")
            print("  Установите: pip install pdf2image")
        
        return status
    
    def is_ready(self) -> bool:
        """Проверить готовность OCR"""
        return self.tesseract_available and self.poppler_available
    
    def install_instructions(self) -> str:
        """Получить инструкции по установке"""
        return """
Для работы OCR необходимо установить:

1. Tesseract-OCR (с русским языком):
   Скачать: https://github.com/UB-Mannheim/tesseract/wiki
   При установке выбрать "Russian" в списке языков
   Добавить в PATH: C:\Program Files\Tesseract-OCR

2. Poppler:
   Скачать: https://github.com/oschwartz10612/poppler-windows/releases
   Распаковать в: C:\poppler
   Добавить в PATH: C:\poppler\bin

3. Python библиотеки:
   pip install pytesseract pdf2image pillow

Проверка установки:
   python -c "import pytesseract; print(pytesseract.get_tesseract_version())"
   python -c "import pytesseract; print('rus' in pytesseract.get_languages())"
"""
    
    def process_pdf(self, pdf_path: str | Path, 
                   save_text: bool = False,
                   output_path: Optional[str] = None) -> str:
        """
        Распознать текст из PDF
        
        Args:
            pdf_path: Путь к PDF файлу
            save_text: Сохранить текст в файл
            output_path: Путь для сохранения (если None - рядом с PDF)
            
        Returns:
            Распознанный текст
        """
        if not self.is_ready():
            print("❌ OCR не готов к работе")
            print(self.install_instructions())
            return ""
        
        pdf_path = Path(pdf_path)
        
        if not pdf_path.exists():
            print(f"❌ Файл не найден: {pdf_path}")
            return ""
        
        print(f"📄 Обработка: {pdf_path.name}")
        print(f"   DPI: {self.dpi}, Язык: {self.lang}")
        
        try:
            from pdf2image import convert_from_path
            import pytesseract
            
            # Конвертируем PDF в изображения
            print(f"   Конвертация в изображения...", end=" ", flush=True)
            images = convert_from_path(pdf_path, dpi=self.dpi, poppler_path=r"C:\poppler\poppler-24.08.0\Library\bin")
            print(f"✓ ({len(images)} стр.)")
            
            # Распознаем каждую страницу
            text_parts = []
            print(f"   OCR распознавание: ", end="", flush=True)
            
            for i, image in enumerate(images, 1):
                page_text = pytesseract.image_to_string(
                    image,
                    lang=self.lang,
                    config='--psm 6'  # Assume a single uniform block of text
                )
                text_parts.append(page_text)
                print(f"{i}", end="", flush=True)
            
            print(" ✓")
            
            # Объединяем и очищаем текст
            full_text = "\n".join(text_parts)
            full_text = self._clean_text(full_text)
            
            print(f"   Результат: {len(full_text):,} символов")
            
            # Сохраняем если нужно
            if save_text:
                if output_path is None:
                    output_path = pdf_path.with_suffix('.txt')
                else:
                    output_path = Path(output_path)
                
                output_path.write_text(full_text, encoding='utf-8')
                print(f"   💾 Сохранено: {output_path}")
            
            return full_text
            
        except Exception as e:
            print(f"\n❌ Ошибка OCR: {e}")
            return ""
    
    def process_directory(self, input_dir: str | Path, 
                         output_dir: Optional[str] = None,
                         pattern: str = "*.pdf") -> List[Dict]:
        """
        Обработать все PDF в папке
        
        Args:
            input_dir: Папка с PDF
            output_dir: Папка для результатов (если None - не сохранять)
            pattern: Маска файлов
            
        Returns:
            Список результатов обработки
        """
        input_dir = Path(input_dir)
        
        if not input_dir.exists():
            print(f"❌ Папка не найдена: {input_dir}")
            return []
        
        pdf_files = list(input_dir.glob(pattern))
        print(f"\n📁 Найдено PDF: {len(pdf_files)}")
        print("=" * 60)
        
        results = []
        
        for i, pdf_file in enumerate(pdf_files, 1):
            print(f"\n[{i}/{len(pdf_files)}] ")
            
            if output_dir:
                out_path = Path(output_dir) / pdf_file.with_suffix('.txt').name
                out_path.parent.mkdir(parents=True, exist_ok=True)
            else:
                out_path = None
            
            text = self.process_pdf(pdf_file, save_text=output_dir is not None, 
                                   output_path=out_path)
            
            results.append({
                'file': str(pdf_file),
                'success': len(text) > 0,
                'chars': len(text),
                'output': str(out_path) if out_path else None
            })
        
        # Статистика
        success_count = sum(1 for r in results if r['success'])
        total_chars = sum(r['chars'] for r in results)
        
        print("\n" + "=" * 60)
        print(f"✅ Обработано: {success_count}/{len(pdf_files)}")
        print(f"📊 Всего символов: {total_chars:,}")
        
        return results
    
    def _clean_text(self, text: str) -> str:
        """Очистить распознанный текст"""
        if not text:
            return ""
        
        # Удаляем лишние пробелы
        text = re.sub(r' +', ' ', text)
        
        # Удаляем пустые строки (больше 2 подряд)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Удаляем артефакты OCR
        text = re.sub(r'[_|]{3,}', '', text)  # Линии
        text = re.sub(r'\f', '\n', text)  # Page breaks
        
        # Удаляем непечатаемые символы
        text = ''.join(char for char in text if char.isprintable() or char in '\n\t')
        
        return text.strip()
    
    def batch_process(self, files: List[str], output_dir: str) -> Dict:
        """
        Пакетная обработка списка файлов
        
        Args:
            files: Список путей к PDF
            output_dir: Папка для результатов
            
        Returns:
            Статистика обработки
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        stats = {
            'total': len(files),
            'success': 0,
            'failed': 0,
            'total_chars': 0,
            'results': []
        }
        
        for i, file_path in enumerate(files, 1):
            print(f"\n[{i}/{len(files)}] {Path(file_path).name}")
            
            out_file = output_dir / Path(file_path).with_suffix('.txt').name
            text = self.process_pdf(file_path, save_text=True, output_path=out_file)
            
            if text:
                stats['success'] += 1
                stats['total_chars'] += len(text)
            else:
                stats['failed'] += 1
            
            stats['results'].append({
                'file': file_path,
                'success': len(text) > 0,
                'chars': len(text)
            })
        
        print("\n" + "=" * 60)
        print("📊 ИТОГИ ПАКЕТНОЙ ОБРАБОТКИ:")
        print(f"   Успешно: {stats['success']}")
        print(f"   Ошибок: {stats['failed']}")
        print(f"   Всего символов: {stats['total_chars']:,}")
        print(f"   Результаты сохранены в: {output_dir}")
        
        return stats


# ========== CLI ИНТЕРФЕЙС ==========

def main():
    """Командная строка для OCR"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='OCR для PDF файлов',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  # Проверить установку
  python ocr_utils.py --check
  
  # Распознать один файл
  python ocr_utils.py document.pdf --output text.txt
  
  # Распознать все PDF в папке
  python ocr_utils.py --directory pdfs/ --output-dir texts/
  
  # С высоким разрешением
  python ocr_utils.py document.pdf --dpi 400 --output text.txt
        """
    )
    
    parser.add_argument('files', nargs='*', help='PDF файлы для обработки')
    parser.add_argument('--check', action='store_true', help='Проверить установку')
    parser.add_argument('--directory', '-d', help='Обработать все PDF в папке')
    parser.add_argument('--output', '-o', help='Файл для сохранения результата')
    parser.add_argument('--output-dir', help='Папка для сохранения результатов')
    parser.add_argument('--dpi', type=int, default=300, help='DPI разрешение (200-400)')
    parser.add_argument('--lang', default='rus', help='Язык (rus, eng, rus+eng)')
    
    args = parser.parse_args()
    
    # Проверка установки
    if args.check:
        print("=" * 60)
        print("ПРОВЕРКА OCR")
        print("=" * 60)
        
        ocr = OCROperator()
        status = ocr._check_dependencies()
        
        print("\nСтатус:")
        for name, ready in status.items():
            icon = "✓" if ready else "✗"
            print(f"  {icon} {name}")
        
        if not ocr.is_ready():
            print("\n" + ocr.install_instructions())
        else:
            print("\n✅ OCR готов к работе!")
        
        return
    
    # Обработка файлов
    ocr = OCROperator(dpi=args.dpi, lang=args.lang)
    
    if not ocr.is_ready():
        print("❌ OCR не готов к работе")
        print(ocr.install_instructions())
        return
    
    # Обработка директории
    if args.directory:
        results = ocr.process_directory(args.directory, args.output_dir)
        return
    
    # Обработка отдельных файлов
    if args.files:
        if len(args.files) == 1 and args.output:
            # Один файл с указанием выхода
            text = ocr.process_pdf(args.files[0], save_text=True, output_path=args.output)
            print(f"\n{'='*60}")
            print("РАСПОЗНАННЫЙ ТЕКСТ (первые 500 символов):")
            print("=" * 60)
            print(text[:500])
            if len(text) > 500:
                print(f"\n... и еще {len(text)-500} символов")
        else:
            # Несколько файлов
            output_dir = args.output_dir or "ocr_output"
            stats = ocr.batch_process(args.files, output_dir)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
