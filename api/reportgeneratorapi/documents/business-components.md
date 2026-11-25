# Business Components Kullanım Rehberi

## 1. Amaç

Bu doküman, React ve TypeScript kullanılarak geliştirilen uygulama ekranlarında aşağıdaki hazır component'lerin doğru şekilde kullanılmasını sağlamak amacıyla hazırlanmıştır.

- `CustomerSearch`
- `GroupSearch`
- `AccountSearch`
- `AskMaya`

Ekran geliştiren yapay zekâ uygulaması, kendisine verilen ekran tanımını veya JSON verisini analiz ederek ihtiyaç duyulan component'leri bu dokümanda açıklanan kurallara göre kullanmalıdır.

### Genel kurallar

1. Hazır component'ler, tanımlandıkları npm paketlerinden import edilmelidir.
2. Component'lerin desteklediği prop'lar kullanılmalıdır.
3. Dokümanda belirtilmeyen prop'lar, callback parametreleri veya metotlar varsayılmamalıdır.
4. Bir component'in zorunlu prop'ları, TypeScript tipleri ve kullanım örnekleri esas alınmalıdır.
5. Callback fonksiyonları component'in beklediği parametre tiplerine uygun yazılmalıdır.
6. Bir component için referans (`ref`) gerekiyorsa ilgili handle tipi kullanılmalıdır.
7. Ekran kodu oluşturulurken component'in işlevi ve özellikleri değiştirilmemelidir.
8. Token, şube numarası ve diğer dinamik değerler mümkün olduğunda ekranın mevcut değişkenlerinden veya uygulamanın sağladığı konfigürasyondan alınmalıdır. Örneklerdeki değerler gerçek ortam değerleri olarak kabul edilmemelidir.

---

# 2. CustomerSearch

## 2.1. Component'in amacı

`CustomerSearch`, müşteri arama işlemlerinde kullanılır.

Müşteri arama alanına ihtiyaç duyulan ekranlarda bu component tercih edilmelidir.

## 2.2. Import işlemleri

```tsx
import { CustomerSearch } from "customercommoncomponents";
import { CustomerSearchHandles } from "customercommoncomponents/build/@types";
```

`CustomerSearch`, müşteri arama arayüzünü oluşturur.

`CustomerSearchHandles`, component'in `ref` üzerinden erişilebilen metotlarının tipini tanımlar.

## 2.3. Desteklenen prop'lar

| Prop | Açıklama |
|---|---|
| `token` | Müşteri arama işlemlerinde kullanılacak token. |
| `loginBranchNo` | Müşteri arama işlemlerinde kullanılacak giriş şubesi numarası. |
| `searchInAllBranch` | Tüm şubelerde arama yapılıp yapılmayacağını belirtir. |
| `openDetailSearch` | Detaylı arama ekranının açılıp açılmayacağını belirtir. |
| `showMessage` | Mesaj gösterilip gösterilmeyeceğini belirtir. |
| `onSearchResult` | Arama sonucu elde edildiğinde tetiklenen callback fonksiyonudur. |
| `onInputChange` | Input değeri değiştiğinde tetiklenen callback fonksiyonudur. |
| `ref` | `CustomerSearchHandles` tipinde referans alır. |

**Not:** Bu tabloda prop'ların zorunlu veya isteğe bağlı olduğu belirtilmemiştir. Bu bilgi, paket içindeki gerçek TypeScript tanımlarından doğrulanmalıdır.

## 2.4. Ref üzerinden kullanılabilen metotlar

`CustomerSearchHandles` referansı üzerinden aşağıdaki metotlar kullanılabilir.

| Metot | Açıklama |
|---|---|
| `getInputValue()` | Input alanındaki mevcut değeri döndürür. |
| `clearInputValue()` | Input alanındaki değeri temizler. |
| `editInputValue()` | Input alanındaki değeri değiştirir. |

`editInputValue()` metodunun parametre tipi ve dönüş tipi bu dokümanda belirtilmemiştir. Metot çağrısı oluşturulurken gerçek TypeScript tanımı kontrol edilmelidir.

## 2.5. Kullanım örneği

```tsx
import { useRef } from "react";

import { CustomerSearch } from "customercommoncomponents";
import { CustomerSearchHandles } from "customercommoncomponents/build/@types";

const CustomerSearchExample = () => {
  const refmyInput = useRef<CustomerSearchHandles>(null);

  const handleCustomerSearchResult = (
    promise: Promise<typeof ICustomerSearchReponse>
  ) => {
    promise.then((value) => {
      console.log(value);
    });
  };

  return (
    <CustomerSearch
      ref={refmyInput}
      token=""
      loginBranchNo={9513}
      searchInAllBranch={true}
      openDetailSearch={true}
      showMessage={true}
      onSearchResult={handleCustomerSearchResult}
      onInputChange={(params: string) => console.log(params)}
    />
  );
};

export default CustomerSearchExample;
```

**Önemli:** Yukarıdaki örnek, sağlanan kullanım örneğinin yapısını korur. `ICustomerSearchReponse` tipinin nereden import edildiği ve gerçek dönüş tipi, ilgili paketin TypeScript tanımlarından doğrulanmalıdır. Bu tipin yazımı örnekteki haliyle korunmuştur.

## 2.6. Ref kullanım örnekleri

### Input değerini okuma

```tsx
const inputValue = refmyInput.current?.getInputValue();
```

### Input değerini temizleme

```tsx
refmyInput.current?.clearInputValue();
```

### Input değerini değiştirme

`editInputValue()` metodu input değerini değiştirmek için kullanılır. Parametre tipi dokümante edilmediğinden, çağrı paketin gerçek tip tanımına göre oluşturulmalıdır.

## 2.7. Callback kuralları

### onSearchResult

Müşteri arama sonucu `Promise` üzerinden işlenir.

```tsx
const handleCustomerSearchResult = (
  promise: Promise<typeof ICustomerSearchReponse>
) => {
  promise.then((value) => {
    console.log(value);
  });
};
```

Ekran oluşturulurken callback'in beklediği parametre yapısı korunmalıdır.

### onInputChange

Input değiştiğinde tetiklenir.

```tsx
onInputChange={(params: string) => {
  console.log(params);
}}
```

Callback parametresi `string` tipindedir.

---

# 3. GroupSearch

## 3.1. Component'in amacı

`GroupSearch`, grup arama işlemleri için kullanılır.

Ekranda grup arama alanına ihtiyaç duyulduğunda bu component tercih edilmelidir.

## 3.2. Import işlemleri

```tsx
import {
  GroupSearch,
  IGroupSearchDetail
} from "customercommoncomponents";

import {
  GroupSearchHandles,
  GroupSearchProps
} from "customercommoncomponents/build/@types/types/interfaces/GroupSearchTypes";
```

- `GroupSearch`: Grup arama component'idir.
- `IGroupSearchDetail`: Grup arama sonucunun detay tipi olarak kullanılır.
- `GroupSearchHandles`: `ref` üzerinden erişilebilen metotların tipidir.
- `GroupSearchProps`: Component prop'larının tipidir.

Bu örnekte `GroupSearchProps` kullanılmamaktadır. Yalnızca ihtiyaç duyuluyorsa import edilmelidir.

## 3.3. Desteklenen prop'lar

| Prop | Açıklama |
|---|---|
| `token` | Grup arama işlemlerinde kullanılacak token. |
| `onSearchResult` | Arama sonucu elde edildiğinde tetiklenen callback fonksiyonudur. |
| `ref` | `GroupSearchHandles` tipinde referans alır. |

## 3.4. Ref üzerinden kullanılabilen metotlar

| Metot | Açıklama |
|---|---|
| `getInputValue()` | Input alanındaki mevcut değeri döndürür. |
| `clearInputValue()` | Input alanındaki değeri temizler. |

`GroupSearch` için bu dokümanda yalnızca yukarıdaki iki metot tanımlanmıştır. Başka metotlar varsayılmamalıdır.

## 3.5. Kullanım örneği

```tsx
import { useRef } from "react";

import {
  GroupSearch,
  IGroupSearchDetail
} from "customercommoncomponents";

import {
  GroupSearchHandles
} from "customercommoncomponents/build/@types/types/interfaces/GroupSearchTypes";

const GroupSearchExample = ({ token }: { token: string }) => {
  const refGroupSearch = useRef<GroupSearchHandles>(null);

  const handleGroupSearchResult = (
    promise: Promise<typeof IGroupSearchDetail>
  ) => {
    promise.then((groupSearchDetail) => {
      console.log(groupSearchDetail);
    });
  };

  return (
    <GroupSearch
      ref={refGroupSearch}
      token={token}
      onSearchResult={handleGroupSearchResult}
    />
  );
};

export default GroupSearchExample;
```

**Önemli:** `typeof IGroupSearchDetail` ifadesi sağlanan örnekteki yapıyı korumaktadır. Gerçek projede `IGroupSearchDetail` bir TypeScript tipi veya arayüzü ise `typeof` kullanımının uygunluğu ve callback'in gerçek dönüş tipi paket tanımlarından kontrol edilmelidir.

## 3.6. Ref kullanım örnekleri

### Input değerini okuma

```tsx
const groupValue = refGroupSearch.current?.getInputValue();
```

### Input değerini temizleme

```tsx
refGroupSearch.current?.clearInputValue();
```

## 3.7. Callback kuralları

`onSearchResult`, grup arama sonucunu içeren bir `Promise` alır.

```tsx
const handleGroupSearchResult = (
  promise: Promise<typeof IGroupSearchDetail>
) => {
  promise.then((groupSearchDetail) => {
    console.log(groupSearchDetail);
  });
};
```

Callback, component'in beklediği biçimde tanımlanmalıdır.

---

# 4. AccountSearch

## 4.1. Component'in amacı

`AccountSearch`, hesap arama işlemlerinde kullanılır.

Ekranda bir hesabın aranması, seçilen hesap değerinin aktarılması veya hesap aramasından sonra ek işlem yürütülmesi gerekiyorsa bu component kullanılmalıdır.

## 4.2. Import işlemleri

```tsx
import { AccountSearch } from "deposit-common-components";
import { IAccountInfoModel } from "deposit-common-components/build/@types";
```

- `AccountSearch`: Hesap arama component'idir.
- `IAccountInfoModel`: Hesap bilgilerini temsil eden tiptir.

## 4.3. Desteklenen prop'lar

| Prop | Açıklama |
|---|---|
| `id` | Hesap arama component'ine benzersiz bir HTML/component kimliği vermek için kullanılır. |
| `token` | Hesap arama işlemlerinde kullanılacak token. |
| `loginBranchNo` | Kullanıcının giriş yaptığı şube numarası. |
| `branchNo` | Şube numarası. |
| `statusCheck` | DRM kontrolünü belirtir. Kontrol varsa `'E'`, yoksa `'H'` kullanılır. |
| `warningCheck` | Hesap bulunduktan sonra uyarı kontrolünün yapılıp yapılmayacağını belirtir. Kontrol varsa `'E'`, yoksa `'H'` kullanılır. |
| `includeAllBranches` | Tüm şubelerin hesaba yönelik arama kapsamına dahil edilip edilmeyeceğini belirtir. Hesap arama popup'ındaki şube seçimini ve validasyonları etkiler. |
| `changeSearchBranch` | Arama şubesinin değişip değişmeyeceğini belirtir. Hesap arama popup'ındaki şube seçimini etkiler. |
| `setAccountValue` | Bulunan hesabın değerini uygulamaya aktarmak için kullanılan fonksiyondur. |
| `onBlur` | Hesap arama işlemleri tamamlandıktan sonra çalıştırılacak işlemler için kullanılan callback fonksiyonudur. |

## 4.4. Şube seçimiyle ilgili özel kural

`includeAllBranches` ve `changeSearchBranch` değerleri birlikte `true` olduğunda, Hesap Arama popup'ında şube alanının ilk değeri **Tüm Şubeler** olarak gösterilir.

```tsx
includeAllBranches={true}
changeSearchBranch={true}
```

Bu iki prop birbirinden bağımsızdır. Her ikisinin de `true` olması, belirtilen özel davranışı sağlar.

## 4.5. Kullanım örneği

```tsx
import { AccountSearch } from "deposit-common-components";

const AccountSearchExample = ({
  token,
  loginBranchNo,
  branchNo,
  setAccountValue,
}: {
  token: string;
  loginBranchNo: number;
  branchNo: number;
  setAccountValue: (...args: any[]) => void;
}) => {
  const onBlur = () => {
    console.log("onBlur işlemi başlatıldı.");
  };

  return (
    <AccountSearch
      id="teb-res-res"
      token={token}
      statusCheck="E"
      loginBranchNo={loginBranchNo}
      branchNo={branchNo}
      warningCheck="E"
      includeAllBranches={true}
      changeSearchBranch={true}
      setAccountValue={setAccountValue}
      onBlur={onBlur}
    />
  );
};

export default AccountSearchExample;
```

**Önemli:** `setAccountValue` fonksiyonunun parametre ve dönüş tipi, burada örneği sadeleştirmek için genel biçimde gösterilmiştir. Gerçek ekran kodunda `any` yerine uygulamadaki fonksiyonun gerçek tipi veya `IAccountInfoModel` ile uyumlu tip kullanılmalıdır. Bu dokümanda belirtilmeyen hesap modeli alanları varsayılmamalıdır.

## 4.6. Callback kuralları

### setAccountValue

Bulunan hesabın değerini uygulamaya aktarmak için kullanılır.

Bu fonksiyon, hesap seçimi sonucunun başka bir state'e, forma veya iş mantığına aktarılması gereken durumlarda kullanılmalıdır.

Fonksiyonun gerçek imzası, mevcut uygulamanın tip tanımlarından alınmalıdır.

### onBlur

Hesap arama işlemleri tamamlandıktan sonra çalıştırılacak ek işlemler için kullanılır.

```tsx
const onBlur = () => {
  console.log("onBlur işlemi başlatıldı.");
};
```

Bu callback, yalnızca gerçekten ihtiyaç duyulan ek işlemler için kullanılmalıdır.

---

# 5. AskMaya

## 5.1. Component'in amacı

`AskMaya`, uygulama ekranına AskMaya bileşenini eklemek için kullanılır.

Sağlanan kullanım örneğinde `AskMaya`, `TebRichHeader` component'inin `centerSlot` alanında gösterilmektedir.

## 5.2. Import işlemi

```tsx
import { AskMaya } from "askmaya";
```

## 5.3. Desteklenen prop'lar

| Prop | Açıklama |
|---|---|
| `id` | AskMaya component'ine verilen kimlik. |
| `token` | AskMaya işlemlerinde kullanılacak token. |
| `apiGatewayUrl` | API Gateway adresi. Örnekte ortam değişkeninden alınır. |

Sağlanan örnekte `apiGatewayUrl`, `process.env.REACT_APP_API_GW_URL` üzerinden alınmaktadır.

## 5.4. Kullanım örneği

```tsx
import { AskMaya } from "askmaya";

<TebRichHeader
  onPrimaryAction={() => console.log()}
  onSecondaryAction={() => console.log()}
  primaryTitle="TEB"
  primaryIcon="user"
  secondaryIcon="logout"
  secondaryTitle="Altyapı Yazılımları"
  infoLabel="Cihan Kirazcı"
  centerSlot={
    <div style={{ marginLeft: "auto" }}>
      <AskMaya
        id="askmayaid"
        token={token}
        apiGatewayUrl={process.env.REACT_APP_API_GW_URL!}
      />
    </div>
  }
  variant={HeaderVariant.filled}
/>
```

## 5.5. Kullanım kuralları

1. `AskMaya`, `askmaya` paketinden import edilmelidir.
2. `id`, `token` ve `apiGatewayUrl` değerleri sağlanmalıdır.
3. `apiGatewayUrl`, uygulamanın mevcut ortam değişkeninden alınmalıdır.
4. `process.env.REACT_APP_API_GW_URL!` ifadesindeki `!`, TypeScript non-null assertion operatörüdür. Ortam değişkeninin gerçekten tanımlı olduğu doğrulanmalıdır.
5. `TebRichHeader` içinde kullanılması zorunlu değildir; ancak farklı yerleşimlerde kullanımın desteklenip desteklenmediği ilgili component'in dokümantasyonundan doğrulanmalıdır.

---

# 6. Component Seçim Rehberi

Ekran oluşturulurken ihtiyaç duyulan işlev aşağıdaki tabloya göre eşleştirilmelidir.

| Ekran ihtiyacı | Kullanılacak component | Paket |
|---|---|---|
| Müşteri arama | `CustomerSearch` | `customercommoncomponents` |
| Grup arama | `GroupSearch` | `customercommoncomponents` |
| Hesap arama | `AccountSearch` | `deposit-common-components` |
| AskMaya bileşenini gösterme | `AskMaya` | `askmaya` |

Birden fazla işlev gerekiyorsa aynı ekranda birden fazla component kullanılabilir.

Örneğin, hem müşteri hem de hesap araması gereken bir ekranda `CustomerSearch` ve `AccountSearch` birlikte kullanılabilir.

---

# 7. Yapay Zekâ ile Ekran Oluşturma Kuralları

Bu dokümanı okuyarak ekran kodu üreten uygulama aşağıdaki kurallara uymalıdır.

## 7.1. Component eşleştirme

Ekran tanımı veya JSON verisi analiz edilerek ihtiyaç duyulan component belirlenmelidir.

- Müşteri arama ihtiyacı varsa `CustomerSearch` kullanılmalıdır.
- Grup arama ihtiyacı varsa `GroupSearch` kullanılmalıdır.
- Hesap arama ihtiyacı varsa `AccountSearch` kullanılmalıdır.
- AskMaya gösterimi isteniyorsa `AskMaya` kullanılmalıdır.

Sadece isim benzerliğine dayanarak component seçilmemelidir. Ekrandaki alanın işlevi esas alınmalıdır.

## 7.2. Import kuralları

Her component kendi paketinden import edilmelidir.

```tsx
import { CustomerSearch } from "customercommoncomponents";
import { GroupSearch } from "customercommoncomponents";
import { AccountSearch } from "deposit-common-components";
import { AskMaya } from "askmaya";
```

Yalnızca ekranda kullanılan component'ler import edilmelidir.

`ref` kullanılacaksa ilgili handle tipi de import edilmelidir.

## 7.3. Prop oluşturma kuralları

1. Yalnızca desteklendiği bilinen prop'lar kullanılmalıdır.
2. Prop isimleri değiştirilmemelidir.
3. String değerler ve boolean değerler doğru tipte verilmelidir.
4. `statusCheck` ve `warningCheck` için `'E'` ve `'H'` değerleri kullanılmalıdır.
5. `token`, `loginBranchNo` ve `branchNo` gibi değişkenler mevcut uygulama bağlamından alınmalıdır.
6. Mevcut değer bilinmiyorsa sahte üretim verileri oluşturulmamalıdır.
7. Eksik bilgi varsa uygulamanın mevcut kodu, tip tanımları veya konfigürasyonu incelenmelidir.
8. Prop'ın zorunluluğu bilinmiyorsa tahmin yapılmamalıdır.

## 7.4. Ref oluşturma kuralları

`CustomerSearch` için:

```tsx
const customerSearchRef = useRef<CustomerSearchHandles>(null);
```

`GroupSearch` için:

```tsx
const groupSearchRef = useRef<GroupSearchHandles>(null);
```

Ref üzerinden yalnızca ilgili component için dokümante edilen metotlar kullanılmalıdır.

`AccountSearch` ve `AskMaya` için bu dokümanda bir handle tipi veya ref metodu tanımlanmamıştır. Bu nedenle gerçek paket tanımları doğrulanmadan bu component'lere ref üzerinden erişim kodu üretilmemelidir.

## 7.5. Callback oluşturma kuralları

Callback'ler component'in beklediği veri yapısına uygun olarak tanımlanmalıdır.

- `CustomerSearch.onSearchResult`: Müşteri arama sonucu.
- `CustomerSearch.onInputChange`: String tipinde input değişikliği.
- `GroupSearch.onSearchResult`: Grup arama sonucu.
- `AccountSearch.setAccountValue`: Bulunan hesap değerinin aktarılması.
- `AccountSearch.onBlur`: Hesap arama sonrası çalıştırılacak işlem.

Callback'lerin gerçek TypeScript imzaları mevcutsa bu imzalar kullanılmalıdır. Eksik imzalar tahmin edilmemelidir.

## 7.6. Mevcut ekran mimarisini koruma

Kod oluşturulurken:

- Mevcut React ve TypeScript yapısı korunmalıdır.
- Projede kullanılan import düzenine uyulmalıdır.
- Uygulamanın mevcut state yönetimi ve form yapısı gereksiz yere değiştirilmemelidir.
- Component'lerin kendi arama ve validasyon davranışları yeniden yazılmamalıdır.
- Hazır component'in işlevini taklit eden yeni bir arama component'i oluşturulmamalıdır.
- Gereksiz bağımlılık veya yeni paket eklenmemelidir.

---

# 8. TypeScript ve Paket Tanımlarının Doğrulanması

Bu doküman, sağlanan kullanım açıklamalarına dayanır. Gerçek ekran kodu üretilirken proje içindeki TypeScript tanımları esas alınmalıdır.

Özellikle aşağıdaki konular doğrulanmalıdır:

1. `CustomerSearch` ve `GroupSearch` callback'lerinin gerçek parametre tipleri.
2. `ICustomerSearchReponse` ve `IGroupSearchDetail` tiplerinin doğru import biçimleri.
3. `CustomerSearchHandles.editInputValue()` metodunun parametreleri.
4. `AccountSearch.setAccountValue` fonksiyonunun imzası.
5. `AccountSearch` prop'larının zorunluluk durumları.
6. `AskMaya` prop'larının TypeScript tanımları.
7. Paket sürümleri ve uygulamanın mevcut React/TypeScript sürümüyle uyumluluk.

Paket tanımları bu dokümandaki örneklerle çelişirse gerçek paket tanımları esas alınmalıdır.

---

# 9. Sonuç

Bu dokümanda tanımlanan dört hazır component, ekran oluşturma sürecinde işlevlerine göre kullanılmalıdır:

- `CustomerSearch`: Müşteri arama.
- `GroupSearch`: Grup arama.
- `AccountSearch`: Hesap arama.
- `AskMaya`: AskMaya bileşenini ekrana yerleştirme.

Yapay zekâ uygulaması, ekran tanımını analiz etmeli, uygun component'i seçmeli, doğru import ve prop'ları kullanmalı ve oluşturduğu kodun TypeScript tipleriyle uyumlu olmasını sağlamalıdır.

Dokümanda bulunmayan davranışlar varsayılmamalı; gerektiğinde gerçek paket tanımları ve mevcut uygulama kodu incelenmelidir.