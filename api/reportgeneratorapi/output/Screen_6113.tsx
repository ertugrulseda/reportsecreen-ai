import React, { useState } from 'react';
import { TebDatePicker, TebAutoComplete, TebRadioButton, TebInput, TebButton, TebLayoutGrid, TebRichHeader, TebCard, TebDataGridEnterprise } from 'basic-ui-lib';
import { HeaderVariant, InputSize, InputType } from 'basic-ui-lib';
import type { ColDef } from 'ag-grid-community';

const ReportScreen: React.FC = () => {
  const [startDate, setStartDate] = useState<Date | null>(null);
  const [endDate, setEndDate] = useState<Date | null>(null);
  const [expenseType, setExpenseType] = useState<string | null>(null);
  const [source, setSource] = useState<'Hesaptan' | 'Müşteriden'>('Hesaptan');
  const [accountNo, setAccountNo] = useState<string>('');
  
  const expenseTypeOptions = [
    { label: 'Kargo Ücreti', value: 'kargo' },
    { label: 'Hizmet Ücreti', value: 'hizmet' },
    { label: 'Diğer', value: 'diger' },
  ];

  const columnDefs: ColDef[] = [
    { field: 'date', headerName: 'Tarih', flex: 1 },
    { field: 'type', headerName: 'Masraf Türü', flex: 1 },
    { field: 'source', headerName: 'Kaynak', flex: 1 },
    { field: 'amount', headerName: 'Tutar', flex: 1 },
    { field: 'account', headerName: 'Hesap No', flex: 1 },
  ];

  const rowData = [
    { date: '2023-05-15', type: 'Kargo Ücreti', source: 'Hesaptan', amount: '25.00', account: '123456' },
    { date: '2023-05-16', type: 'Hizmet Ücreti', source: 'Müşteriden', amount: '150.00', account: '789012' },
  ];

  return (
    <TebLayoutGrid container spacing='4px' columns={24}>
      <TebLayoutGrid child columns={24}>
        <TebRichHeader 
          variant={HeaderVariant.filled}
          primaryTitle="TEB"
          secondaryTitle="82-92 Tehsil Edilen Masraf Komisyonlar"
          infoLabel="Seda Ertuğrul"
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
              size={InputSize.medium}
              disabled={false}
              error={false}
              noOptionsText="Seçenek bulunamadı"
              getOptionLabel={(option: typeof expenseTypeOptions[0]) => option.label}
              isOptionEqualToValue={(option, value) => option.value === value}
            />
            
            <TebRadioButton
              id="source-account"
              name="source"
              label="Hesaptan"
              checked={source === 'Hesaptan'}
              onChange={(checked) => checked && setSource('Hesaptan')}
            />
            
            <TebRadioButton
              id="source-customer"
              name="source"
              label="Müşteriden"
              checked={source === 'Müşteriden'}
              onChange={(checked) => checked && setSource('Müşteriden')}
            />
            
            <TebInput
              id="account-no"
              type={InputType.text}
              value={accountNo}
              onInputChange={(e) => setAccountNo(e.target.value)}
              placeholder="Hesap No"
              size={InputSize.medium}
              tabIndex={0}
            />
            
            <TebButton 
              size={InputSize.medium}
              variant="primary"
              type="button"
              onClick={() => console.log('Ara clicked')}
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
                setSource('Hesaptan');
                setAccountNo('');
              }}
            >
              Temizle
            </TebButton>
          </div>
        </TebCard>
      </TebLayoutGrid>
      
      <TebLayoutGrid child lg={18} md={18} sm={18}>
        <TebDataGridEnterprise
          columnDefs={columnDefs}
          rowData={rowData}
          domLayout='normal'
          style={{ width: '100%', height: '100%' }}
        />
      </TebLayoutGrid>
    </TebLayoutGrid>
  );
};

export default ReportScreen;