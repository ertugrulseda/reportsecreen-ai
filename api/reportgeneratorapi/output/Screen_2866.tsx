import React, { useState } from 'react';
import { TebDatePicker, TebAutoComplete, TebRadioButton, TebInput, TebButton } from 'basic-ui-lib';
import { TebRichHeader, TebCard, TebDataGridEnterprise, TebLayoutGrid } from 'basic-ui-lib';
import { HeaderVariant, InputSize, InputType } from 'basic-ui-lib';
import type { ColDef } from 'ag-grid-community';

const ReportScreen: React.FC = () => {
  const [startDate, setStartDate] = useState<Date | null>(null);
  const [endDate, setEndDate] = useState<Date | null>(null);
  const [expenseType, setExpenseType] = useState<string | null>(null);
  const [accountSource, setAccountSource] = useState<string>('Hesaptan');
  const [accountNumber, setAccountNumber] = useState<string>('');
  
  const expenseTypeOptions = [
    'Yemek Masrafı',
    'Ulaşım Masrafı',
    'Konaklama Masrafı',
    'Diğer'
  ];

  const columnDefs: ColDef[] = [
    { field: 'işlem Tarihi', headerName: 'işlem Tarihi', flex: 1 },
    { field: 'İşlem No', headerName: 'İşlem No', flex: 1 },
    { field: 'Muhasebe no', headerName: 'Muhasebe no', flex: 1 },
    { field: 'Hesap No', headerName: 'Hesap No', flex: 1 },
    { field: 'İşlem Tutar', headerName: 'İşlem Tutar', flex: 1 },
    { field: 'Açıklama', headerName: 'Açıklama', flex: 1 }
  ];

  const rowData = [
    {
      'işlem Tarihi': '2023-05-15',
      'İşlem No': 'ISL-001',
      'Muhasebe no': 'MUH-12345',
      'Hesap No': 'TR001234567890',
      'İşlem Tutar': '500.00',
      'Açıklama': 'Yemek masrafı ödemesi'
    }
  ];

  return (
    <TebLayoutGrid container spacing='4px' columns={24}>
      <TebLayoutGrid child columns={24}>
        <TebRichHeader 
          variant={HeaderVariant.filled}
          primaryTitle="TEB"
          secondaryTitle="Tahsil Edilen Masra ve Komisyonlar"
          infoLabel="P36516"
          primaryIcon=""
          secondaryIcon=""
          onPrimaryAction={() => { console.log('primary action clicked'); }}
          onSecondaryAction={() => { console.log('secondary action clicked'); }}
        />
      </TebLayoutGrid>
      
      <TebLayoutGrid child lg={6} md={6} sm={6} style={{ margin: '4px' }}>
        <TebCard>
          <div style={{ width: '100%', display: 'flex', flexDirection: 'column', gap: '16px', paddingTop: '8px', boxSizing: 'border-box' }}>
            <TebDatePicker
              label="Başlangıç"
              value={startDate}
              onChange={(date) => setStartDate(date)}
              size={InputSize.medium}
            />
            
            <TebDatePicker
              label="Bitiş"
              value={endDate}
              onChange={(date) => setEndDate(date)}
              size={InputSize.medium}
            />
            
            <TebAutoComplete
              label="Masraf Türü"
              options={expenseTypeOptions}
              value={expenseType}
              onChange={(event, value) => setExpenseType(value)}
              disabled={false}
              error={false}
              size={InputSize.medium}
              noOptionsText="Seçenek bulunamadı"
            />
            
            <TebRadioButton
              id="radio-hesaptan"
              name="accountSource"
              label="Hesaptan"
              checked={accountSource === 'Hesaptan'}
              onChange={(checked) => checked && setAccountSource('Hesaptan')}
            />
            
            <TebRadioButton
              id="radio-musteriden"
              name="accountSource"
              label="Müşteriden"
              checked={accountSource === 'Müşteriden'}
              onChange={(checked) => checked && setAccountSource('Müşteriden')}
            />
            
            <TebInput
              id="account-number"
              type={InputType.text}
              value={accountNumber}
              onInputChange={(e) => setAccountNumber(e.target.value)}
              placeholder="Hesap No"
              size={InputSize.medium}
              tabIndex={0}
            />
            
            <div style={{ display: 'flex', gap: '8px' }}>
              <TebButton
                size={InputSize.medium}
                variant="primary"
                type="button"
                onClick={() => console.log('Filtrele')}
              >
                Ara
              </TebButton>
              
              <TebButton
                size={InputSize.medium}
                variant="secondary"
                type="button"
                onClick={() => {
                  setStartDate(null);
                  setEndDate(null);
                  setExpenseType(null);
                  setAccountSource('Hesaptan');
                  setAccountNumber('');
                }}
              >
                Temizle
              </TebButton>
            </div>
          </div>
        </TebCard>
      </TebLayoutGrid>
      
      <TebLayoutGrid child lg={18} md={18} sm={18}>
        <TebDataGridEnterprise
          columnDefs={columnDefs}
          rowData={rowData}
          style={{ height: '100%', width: '100%' }}
        />
      </TebLayoutGrid>
    </TebLayoutGrid>
  );
};

export default ReportScreen;