import React, { useState } from 'react';
import {
  TebAutoComplete,
  TebInput,
  TebDatePicker,
  TebButton,
  TebLayoutGrid,
  TebRichHeader,
  TebCard,
  TebDataGridEnterprise,
  InputSize,
  HeaderVariant,
  ButtonType,
  ButtonVariant,
  InputType,
} from 'basic-ui-lib';

const ReportScreen: React.FC = () => {
  // State for input fields
  const [ogrenciNo, setOgrenciNo] = useState('');
  const [tcKimlikNo, setTcKimlikNo] = useState('');
  const [tebKayitNo, setTebKayitNo] = useState('');
  
  // State for autocomplete fields
  const [kurum, setKurum] = useState<string | null>(null);
  const [planDurumu, setPlanDurumu] = useState<string | null>(null);
  
  // State for date pickers
  const [baslangicTarihi, setBaslangicTarihi] = useState<Date | null>(null);
  const [bitisTarihi, setBitisTarihi] = useState<Date | null>(null);

  // Mock data for autocomplete options
  const kurumOptions = [
    'İstanbul Üniversitesi',
    'Boğaziçi Üniversitesi',
    'ODTÜ',
    'Ankara Üniversitesi',
    'Ege Üniversitesi',
  ];

  const planDurumuOptions = [
    'Aktif',
    'Pasif',
    'Tamamlandı',
    'Askıda',
    'İptal Edildi',
  ];

  // Mock data for data grid
  const mockRowData = [
    {
      ogrenciAdi: 'Ahmet Yılmaz',
      ogrenciNo: '123456',
      tcKimlikNo: '12345678901',
      kayitTarihi: '2023-01-15',
      durum: 'Aktif',
      tutar: '1500 TL',
    },
    {
      ogrenciAdi: 'Ayşe Kaya',
      ogrenciNo: '789012',
      tcKimlikNo: '98765432109',
      kayitTarihi: '2023-02-20',
      durum: 'Pasif',
      tutar: '1200 TL',
    },
    {
      ogrenciAdi: 'Mehmet Demir',
      ogrenciNo: '345678',
      tcKimlikNo: '45678912345',
      kayitTarihi: '2023-03-10',
      durum: 'Tamamlandı',
      tutar: '1800 TL',
    },
    {
      ogrenciAdi: 'Fatma Şahin',
      ogrenciNo: '901234',
      tcKimlikNo: '78912345678',
      kayitTarihi: '2023-04-05',
      durum: 'Aktif',
      tutar: '2000 TL',
    },
    {
      ogrenciAdi: 'Mustafa Koç',
      ogrenciNo: '567890',
      tcKimlikNo: '32165498701',
      kayitTarihi: '2023-05-12',
      durum: 'Askıda',
      tutar: '1600 TL',
    },
  ];

  const columnDefs = [
    { headerName: 'Öğrenci Adı', field: 'ogrenciAdi', flex: 1 },
    { headerName: 'Öğrenci No', field: 'ogrenciNo', flex: 1 },
    { headerName: 'T.C. Kimlik No', field: 'tcKimlikNo', flex: 1 },
    { headerName: 'Kayıt Tarihi', field: 'kayitTarihi', flex: 1 },
    { headerName: 'Durum', field: 'durum', flex: 1 },
    { headerName: 'Tutar', field: 'tutar', flex: 1 },
  ];

  return (
    <TebLayoutGrid container spacing='4px' columns={24}>
      <TebLayoutGrid child columns={24}>
        <TebRichHeader
          variant={HeaderVariant.filled}
          primaryTitle='TEB'
          secondaryTitle='Okul Tahsilatlari Gözlem'
          infoLabel=''
          primaryIcon=''
          secondaryIcon=''
          onPrimaryAction={() => {
            console.log('primary action clicked');
          }}
          onSecondaryAction={() => {
            console.log('secondary action clicked');
          }}
        />
      </TebLayoutGrid>
      
      <TebLayoutGrid child lg={6} md={6} sm={6} style={{ margin: '4px' }}>
        <TebCard>
          <div
            style={{
              width: '100%',
              display: 'flex',
              flexDirection: 'column',
              gap: '16px',
              paddingTop: '8px',
              boxSizing: 'border-box',
            }}
          >
            <TebAutoComplete
              id='kurum-select'
              label='Kurum'
              options={kurumOptions}
              value={kurum}
              disabled={false}
              error={false}
              size={InputSize.medium}
              noOptionsText='Sonuç bulunamadı'
              onChange={(event, value) => setKurum(value)}
              inputValue=''
              tabIndex={0}
            />
            
            <TebInput
              id='ogrenci-no-input'
              value={ogrenciNo}
              type={InputType.text}
              tabIndex={0}
              size={InputSize.medium}
              placeholder='Ögrenci No'
              onInputChange={(e) => setOgrenciNo(e.target.value)}
            />
            
            <TebInput
              id='tc-kimlik-no-input'
              value={tcKimlikNo}
              type={InputType.text}
              tabIndex={0}
              size={InputSize.medium}
              placeholder='T.C.Kimlik No'
              onInputChange={(e) => setTcKimlikNo(e.target.value)}
            />
            
            <TebDatePicker
              value={baslangicTarihi}
              label='Tarih Araligi Başlangıç Tarihi'
              onChange={(date) => setBaslangicTarihi(date)}
            />
            
            <TebDatePicker
              value={bitisTarihi}
              label='Tarih Araligi Bitiş Tarihi'
              onChange={(date) => setBitisTarihi(date)}
            />
            
            <TebInput
              id='teb-kayit-no-input'
              value={tebKayitNo}
              type={InputType.text}
              tabIndex={0}
              size={InputSize.medium}
              placeholder='TEB Kayit No'
              onInputChange={(e) => setTebKayitNo(e.target.value)}
            />
            
            <TebAutoComplete
              id='plan-durumu-select'
              label='Plan Durumu'
              options={planDurumuOptions}
              value={planDurumu}
              disabled={false}
              error={false}
              size={InputSize.medium}
              noOptionsText='Sonuç bulunamadı'
              onChange={(event, value) => setPlanDurumu(value)}
              inputValue=''
              tabIndex={0}
            />
            
            <TebButton
              size={InputSize.medium}
              variant={ButtonVariant.primary}
              type={ButtonType.button}
              onClick={() => console.log('Filtrele button clicked')}
            >
              Filtrele
            </TebButton>
          </div>
        </TebCard>
      </TebLayoutGrid>
      
      <TebLayoutGrid child lg={18} md={18} sm={18}>
        <TebDataGridEnterprise
          className='ag-theme-quartz'
          columnDefs={columnDefs}
          rowData={mockRowData}
          domLayout='normal'
        />
      </TebLayoutGrid>
    </TebLayoutGrid>
  );
};

export default ReportScreen;