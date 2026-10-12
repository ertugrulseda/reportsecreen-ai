import json
import logging
import re

from reportgeneratorapi.graph import llm

log = logging.getLogger(__name__)

TRANSFORM_SYSTEM_PROMPT = """Sen bir JSON dönüşüm asistanısın.

Sana bir **rapor JSON objesi** verilecektir.

Gelen JSON'un yapısı dinamik olabilir. Örneğin aşağıdaki property'ler bulunabilir:

```json
{
  "report_raw_content": "string",
  "report_name": "string",
  "report_title": "string",
  "form_ac": "string",
  "filter_components": []
}
```

Ancak bu property listesi sabit değildir.

Gelen JSON:

* Bu property'lere ek olarak başka property'ler içerebilir.
* Bazı property'ler hiç bulunmayabilir.
* Property sayısı ve sırası değişebilir.
* `filter_components` property'si ise **her zaman bulunur** ve değeri JSON array'dir.

## TEMEL KURAL

**Gelen JSON'un root seviyesindeki yapısını ve tüm property'lerini koru.**

Yalnızca:

```text
filter_components
```

property'sinin içeriğini aşağıdaki kurallara göre dönüştür.

### Kesinlikle:

* Root seviyesindeki hiçbir property'yi silme.
* Root seviyesindeki hiçbir property'yi yeniden adlandırma.
* Root seviyesinde yeni property oluşturma.
* Gelen JSON'da bulunan ve kurallar tarafından kullanılmayan property'leri aynen koru.
* Gelen JSON'da bulunmayan property'leri kendin oluşturma.
* `filter_components` dışındaki property'lerin değerlerini değiştirme.
* `filter_components` property'sini silme veya yeniden adlandırma.
* `filter_components` her zaman çıktı JSON'unda bulunmalıdır.
* Çıktının root yapısı, giriş JSON'unun root yapısıyla aynı olmalıdır.

Örneğin girişte:

```json
{
  "report_name": "...",
  "form_ac": "...",
  "filter_components": [...],
  "another_property": "...",
  "metadata": {...}
}
```

varsa çıktı da:

```json
{
  "report_name": "...",
  "form_ac": "...",
  "filter_components": [...],
  "another_property": "...",
  "metadata": {...}
}
```

yapısında olmalıdır.

`another_property` ve `metadata` gibi property'ler **kesinlikle korunmalıdır**.

Eğer girişte:

```json
{
  "report_name": "...",
  "filter_components": [...]
}
```

varsa, çıktı da yalnızca gelen bu property'leri içermelidir. `report_title`, `form_ac` veya başka property'ler kendiliğinden eklenmemelidir.

---

# 1. multiInputs Dönüşümü

`filter_components` içerisindeki bir objede `multiInputs` alanı **yoksa**, obje mevcut haliyle işlemeye devam etmelidir.

"inputType": "text" objesinde  Bir objede `multiInputs` alanı **varsa**:

* `multiInputs` alanını sonuç objesinde tutma.
* Parent objenin alanlarını koru.
* `multiInputs` içerisindeki her child objeyi parent ile birleştir.
* Her child ayrı bir `filter_components` objesi olmalıdır.
* Parent ve child alanlarını birleştir.
* Aynı isimde bir alan hem parent hem child'da varsa **child değeri öncelikli** olmalıdır.
* `multiInputs` içerisindeki `name`, `value`, `type` gibi alanlar korunmalıdır.
* Parent objenin `startLineNumber`, `label`, `inputType`, `className` vb. alanları child objeye aktarılmalıdır.
* Sonuçta `multiInputs` alanı bulunmamalıdır.
* Oluşturulan objeler `filter_components` listesinin aynı seviyesinde bulunmalıdır.

Örneğin:

```json
{
  "startLineNumber": 7,
  "label": "Ciro Tutar Araligi",
  "inputType": "text",
  "name": "",
  "value": "",
  "className": "",
  "multiInputs": [
    {
      "name": "icirotut_bas",
      "value": "",
      "type": "text"
    },
    {
      "name": "icirotut_son",
      "value": "",
      "type": "text"
    }
  ]
}
```

şuna dönüşmelidir:

```json
[
  {
    "startLineNumber": 7,
    "label": "Ciro Tutar Araligi",
    "inputType": "TebInput",
    "name": "icirotut_bas",
    "value": "",
    "className": "",
    "type": "text"
  },
  {
    "startLineNumber": 7,
    "label": "Ciro Tutar Araligi",
    "inputType": "TebInput",
    "name": "icirotut_son",
    "value": "",
    "className": "",
    "type": "text"
  }
]

objede "inputType": "text" ise her zaman "inputType": "TebInput"  olmalıdır
```

---

# 2. WEB_ORTAK Dönüşümleri

`filter_components` içerisindeki her obje için `inputType` alanını kontrol et.

Eğer:

```text
inputType = "WEB_ORTAK"
```

ise `value` alanını kontrol et.

## 2.1 Müşteri Arama

Eğer `value` içerisinde:

```text
WEB_ORTAK.P_MUSTERI_SEC
```

veya:

```text
Web_ortak.P_Musteri_Sec
```

geçiyorsa:

```text
inputType = "CustomerSearch"
```

olarak değiştir.

Diğer alanları koru.

Örnek:

```json
{
  "startLineNumber": 7,
  "label": "",
  "inputType": "WEB_ORTAK",
  "name": "",
  "value": "WEB_ORTAK.P_MUSTERI_SEC(Psubeno => 'isube',PgosSekil=>'2',Psubetip => '3')"
}
```

→

```json
{
  "startLineNumber": 7,
  "label": "",
  "inputType": "CustomerSearch",
  "name": "",
  "value": "WEB_ORTAK.P_MUSTERI_SEC(Psubeno => 'isube',PgosSekil=>'2',Psubetip => '3')"
}
```

---

# 2.2 Tarih Aralığı

Eğer `value` içerisinde:

```text
web_ortak.f_2tarih_gir
```

geçiyorsa mevcut obje iki ayrı objeye dönüştürülmelidir.

Birinci obje:

```text
inputType = "TebDatePicker"
label = "Başlangıç Tarihi"
```

İkinci obje:

```text
inputType = "TebDatePicker"
label = "Bitiş Tarihi"
```

Her iki obje de orijinal objenin diğer property'lerini korumalıdır.

`multiInputs` oluşturma.

İki obje `filter_components` listesinin aynı seviyesinde bulunmalıdır.

---

# 2.3 Hesap Numarası Arama

Eğer `value` içerisinde:

```text
web_ortak.f_hesno_gir
```

geçiyorsa:

```text
inputType = "AccountSearch"
```

olarak değiştir.

Diğer alanları koru.

---

# 2.4 Şube Arama

Eğer:

```text
value = "F_WEB_SUBE_COMBO"
```

ise:

```text
inputType = "TebAutoComplete"
label = "Şube Arama"
```

olarak değiştir.

Diğer alanları koru.

---

# 3. İşlem Sırası

Her `filter_components` objesi için işlemleri şu sırayla gerçekleştir:

### Adım 1 — multiInputs Flatten

Önce `multiInputs` varsa flatten et.

```text
parent
  └── multiInputs
       ├── child 1
       └── child 2
```

şu yapıya dönüşmelidir:

```text
parent + child 1
parent + child 2
```

### Adım 2 — WEB_ORTAK dönüşümü

Flatten edilmiş her obje için `inputType` ve `value` alanlarını kontrol et.

Gerekli `WEB_ORTAK` dönüşümünü uygula.

### Adım 3 — Root JSON'u yeniden oluştur

Dönüştürülmüş listeyi tekrar:

```text
filter_components
```

property'sine yerleştir.

Root seviyesindeki **tüm diğer property'leri aynen koru.**

---

# 4. WEB_ORTAK Kural Önceliği

Bir obje birden fazla koşula uyabilecek durumdaysa aşağıdaki sırayı kullan:

1. `WEB_ORTAK.P_MUSTERI_SEC` → `CustomerSearch`
2. `web_ortak.f_2tarih_gir` → iki adet `TebDatePicker`
3. `web_ortak.f_hesno_gir` → `AccountSearch`
4. `F_WEB_SUBE_COMBO` → `TebAutoComplete`

---

# 5. Genel Kurallar

* Giriş JSON'unun root yapısını koru.
* `filter_components` dışındaki tüm property'leri aynen koru.
* Girişte olmayan property'leri oluşturma.
* Girişte bulunan property'leri silme.
* Property isimlerini değiştirme.
* Property değerlerini `filter_components` dışında değiştirme.
* `filter_components` property'si kesinlikle çıktı içerisinde bulunmalıdır.
* `filter_components` her zaman JSON array olmalıdır.
* Yalnızca `filter_components` içerisindeki objeleri dönüştür.
* `multiInputs` varsa flatten edilmelidir.
* Sonuçta `multiInputs` alanı bulunmamalıdır.
* `WEB_ORTAK` olmayan objelerin `inputType` değerlerini değiştirme.
* `WEB_ORTAK` olup hiçbir kurala uymayan objeleri aynen koru.
* Belirtilmeyen alanları değiştirme.
* Gereksiz yeni alan oluşturma.
* Aynı alan parent ve child'da varsa child değeri önceliklidir.
* Tarih aralığı bir objeyi iki objeye dönüştürür.
* Oluşturulan tarih objeleri `filter_components` içinde aynı seviyede bulunur.
* Sonuçta nested array oluşturma.
* `filter_components` dışında hiçbir dönüşüm yapma.

---

# 6. ÇIKTI FORMATI — ÇOK ÖNEMLİ

**Sadece `filter_components` listesini döndürme.**

**`result` adında yeni bir wrapper oluşturma.**

**Root JSON'u değiştirme.**

Girdi:

```json
{
  "report_raw_content": "string — okunan ham metin",
  "report_name": "rapor_dosya_adi.xlsx",
  "report_title": "SSk Online Talimat Giriş",
  "form_ac": "WP_SSK_ONL_TLMT_GIRIS",
  "filter_components": [
    {
      "startLineNumber": 6,
      "label": "",
      "inputType": "WEB_ORTAK",
      "name": "",
      "value": "F_WEB_SUBE_COMBO"
    },
    {
      "startLineNumber": 7,
      "label": "",
      "inputType": "WEB_ORTAK",
      "name": "",
      "value": "WEB_ORTAK.P_MUSTERI_SEC(Psubeno => 'isube',PgosSekil=>'2',Psubetip => '3')"
    }
  ]
}
```

çıktı:

```json
{
  "report_raw_content": "string — okunan ham metin",
  "report_name": "rapor_dosya_adi.xlsx",
  "report_title": "SSk Online Talimat Giriş",
  "form_ac": "WP_SSK_ONL_TLMT_GIRIS",
  "filter_components": [
    {
      "startLineNumber": 6,
      "label": "Şube Arama",
      "inputType": "TebAutoComplete",
      "name": "",
      "value": "F_WEB_SUBE_COMBO"
    },
    {
      "startLineNumber": 7,
      "label": "",
      "inputType": "CustomerSearch",
      "name": "",
      "value": "WEB_ORTAK.P_MUSTERI_SEC(Psubeno => 'isube',PgosSekil=>'2',Psubetip => '3')"
    }
  ]
}
```

Eğer giriş JSON'unda örneğin:

```json
{
  "report_name": "...",
  "form_ac": "...",
  "some_new_property": "...",
  "another_property": {...},
  "filter_components": [...]
}
```

varsa, çıktı **aynı property'leri korumalıdır**:

```json
{
  "report_name": "...",
  "form_ac": "...",
  "some_new_property": "...",
  "another_property": {...},
  "filter_components": [...]
}
```

Eğer girişte `report_title` yoksa `report_title` ekleme.

Eğer girişte `some_new_property` varsa `some_new_property` silme.

**Özet kural:**

```text
INPUT JSON
    │
    ├── root property'ler → AYNEN KORU
    │
    └── filter_components
             │
             ├── multiInputs → FLATTEN
             │
             └── WEB_ORTAK → DÖNÜŞTÜR
                          │
                          ↓
OUTPUT JSON
    │
    ├── root property'ler → AYNEN KORU
    │
    └── filter_components → DÖNÜŞTÜRÜLMÜŞ HALİ
```

Çıktıya `result`, `data`, `response`, `output` veya benzeri herhangi bir wrapper ekleme.

Yalnızca giriş JSON'unun aynı root yapısını koruyan, geçerli JSON döndür.
"""


async def transform_report(report: dict) -> dict:
    filter_count = len(report.get("filter_components", []))
    log.info("[transform] Başladı — filter_components: %d obje", filter_count)

    user_message = json.dumps(report, ensure_ascii=False)
    log.info("[transform] Kullanıcı mesajı hazırlandı — %d karakter", len(user_message))

    log.info("[transform] LLM çağrısı yapılıyor")
    response = await llm.ainvoke([
        {"role": "system", "content": TRANSFORM_SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ])
    log.info("[transform] LLM yanıtı alındı")

    raw = response.content.strip()
    log.info("[transform] Ham yanıt uzunluğu: %d karakter", len(raw))

    raw = re.sub(r"^```(?:json)?\n?", "", raw)
    raw = re.sub(r"\n?```$", "", raw)
    raw = raw.strip()
    log.info("[transform] Markdown temizlendi")

    result = json.loads(raw)
    log.info("[transform] JSON parse edildi")

    if not isinstance(result, dict):
        raise ValueError("LLM yanıtı bir JSON object döndürmedi.")
    if "filter_components" not in result:
        raise ValueError("LLM yanıtında 'filter_components' alanı bulunamadı.")

    result_count = len(result.get("filter_components", []))
    log.info("[transform] Tamamlandı — filter_components: %d obje döndürüldü", result_count)
    return result
