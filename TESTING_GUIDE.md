"""
# Görsel Test Stratejisi - pygame-widget-kit

## Nedir? (What is Visual Testing?)
Görsel testler, uygulamanızın render edilen çıktısını kontrol eder. 
Pixel-perfect testler yapabilir ya da screenshot'ları karşılaştırabilirsiniz.

## Niçin Gerekli? (Why needed?)
- Yeni özellik eklediğinizde UI'nin beklenmedik şekilde değişip değişmediğini tespit etmek
- Regression yakalamak (eski özelliklerin bozulması)
- Farklı ekran çözünürlüklerinde tutarlılık sağlamak

## Implementasyon Stratejileri

### 1. **Screenshot Comparison (Basit & Etkili)**
```python
import pygame
from PIL import Image

# Reference screenshot'ı kaydet (ilk kez)
def save_reference(widget, filename):
    surface = pygame.display.set_mode((800, 600))
    widget.draw(surface)
    image = pygame.image.tostring(surface, "RGB")
    img = Image.frombytes("RGB", (800, 600), image)
    img.save(f"tests/references/{filename}.png")

# Test'te karşılaştır
def test_button_appearance():
    button = Button(text_str="Test", pos=(10, 10), size=(100, 50))
    surface = pygame.display.set_mode((800, 600))
    button.draw(surface)
    
    # Basit pixel buffer karşılaştırması
    assert_visual_match(surface, "button_test.png", tolerance=0.95)
```

### 2. **Bounding Box & Rect Verification**
```python
def test_button_position():
    button = Button(text_str="Test", pos=(50, 50), size=(100, 50))
    
    assert button.absolute_rect[0] == 50  # x
    assert button.absolute_rect[1] == 50  # y
    assert button.absolute_rect[2] == 100 # width
    assert button.absolute_rect[3] == 50  # height
```

### 3. **Color & Style Verification**
```python
def test_button_colors():
    button = Button(
        text_str="Test",
        color=(200, 100, 50),
        hover_color=(220, 120, 70)
    )
    
    assert button.color == (200, 100, 50)
    assert button.hover_color == (220, 120, 70)
```

### 4. **Component Rendering State**
```python
def test_visibility_rendering():
    button = Button(text_str="Test")
    
    button.visible = False
    # Gizli bileşen çizilmemeli
    
    button.visible = True
    # Görünür bileşen çizilmeli
```

## Otomatik Test Çalıştırma

### Global Setup
```bash
# Tüm testleri çalıştır
pytest tests/ -v

# Sadece görsel testleri çalıştır
pytest tests/ -v -m visual

# Coverage raporu ile
pytest tests/ --cov=src/pygame_widget_kit --cov-report=html
```

### CI/CD Pipeline (GitHub Actions)
Workflow file: `.github/workflows/tests.yml`

Her push ve PR'da otomatik olarak:
- Python 3.9, 3.10, 3.11, 3.12'de testleri çalıştır
- Coverage raporunu oluştur
- Test sonuçlarını rapor et

## Gelecek İyileştirmeler

1. **Snapshot Testing** - Reference screenshots oluştur ve karşılaştır
2. **OpenCV Integration** - Template matching ile görsel benzerlik kontrolü
3. **Perceptual Image Comparison** - Pixel-perfect değil, görsel olarak benzer
4. **Performance Testing** - Render hızı ve bellek kullanımını test et
5. **Multi-resolution Testing** - Farklı ekran boyutlarında testler

## Hızlı Start

```bash
# 1. Test dosyaları oluştur (zaten yapıldı!)
# 2. Testleri çalıştır
pytest tests/ -v

# 3. Coverage raporu gör
pytest tests/ --cov=src/pygame_widget_kit --cov-report=html
open htmlcov/index.html

# 4. Git'e push et (CI/CD otomatik çalışacak)
git add tests/
git commit -m "Add comprehensive tests"
git push
```
"""
