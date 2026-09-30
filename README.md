# 🎬 Asu-Player

**Asu-Player**, Python ve PyQt6 kullanılarak geliştirilen, yerel video dosyalarını bölüm mantığıyla oynatmaya yönelik basit ve kullanışlı bir video oynatıcıdır.

Özellikle anime ve dizi bölümlerini düzenli şekilde oynatmak için tasarlanmıştır.

## ✨ Özellikler

- 📁 Klasör seçerek videoları otomatik bulma
- 🎞️ Bölüm numarasına göre otomatik sıralama
- ▶️ Oynat / durdur
- ⏪ 10 saniye geri sarma
- ⏩ 10 saniye ileri sarma
- 🔊 Ses seviyesi kontrolü
- 🔇 Sessize alma
- ⛶ Tam ekran modu
- 🖱️ Video üzerine tek tıklama → Oynat / Durdur
- 🖱️ Video üzerine çift tıklama → Tam ekran
- ⌨️ Klavye kısayolları
- 📺 Bölüm sonunda otomatik sonraki bölüme geçiş
- 👉 Oynatılan bölümü listede gösterme
- ⏱️ Video süresi ve oynatma konumu göstergesi

## 🎮 Klavye Kısayolları

| Tuş | İşlev |
|---|---|
| `Space` | Oynat / Durdur |
| `F` | Tam ekran |
| `Esc` | Tam ekrandan çık |
| `←` | 10 saniye geri |
| `→` | 10 saniye ileri |

## 📂 Desteklenen Video Formatları

- `.mkv`
- `.mp4`
- `.avi`
- `.mov`
- `.webm`

## 📑 Bölüm İsimlendirme

Asu-Player, dosya adının başındaki sayıyı bölüm numarası olarak algılar.

Örneğin:

```text
1.Girls Und Panzer.mkv
2.Girls Und Panzer.mkv
3.Girls Und Panzer.mkv
10.Girls Und Panzer.mkv
