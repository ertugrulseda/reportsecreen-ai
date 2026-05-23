import React, { useState } from 'react';
import {
  TebInput,
  TebAutoComplete,
  TebChip,
  TebRichHeader,
  TebCard,
  TebDataGridEnterprise,
  TebLayoutGrid,
  InputSize,
  InputType,
  HeaderVariant,
} from 'basic-ui-lib';
import { ColDef } from 'ag-grid-community';

interface AutocompleteOption {
  label: string;
  value: string;
}

const RaporEkrani: React.FC = () => {
  const [inputValue, setInputValue] = useState<string>('');
  const [autocompleteValue, setAutocompleteValue] =
    useState<AutocompleteOption | null>(null);
  const [chips, setChips] = useState<string[]>(['Etiket 1', 'Etiket 2']);
  const [autocompleteInputValue, setAutocompleteInputValue] = useState<string>('');

  const autocompleteOptions: AutocompleteOption[] = [
    { label: 'Seçenek 1', value: 'option1' },
    { label: 'Seçenek 2', value: 'option2' },
    { label: 'Seçenek 3', value: 'option3' },
  ];

  const columnDefs: ColDef[] = [
    { headerName: 'Rapor Adı', field: 'name', flex: 1 },
    { headerName: 'Oluşturma Tarihi', field: 'date', flex: 1 },
    { headerName: 'Durum', field: 'status', flex: 1 },
  ];

  const rowData = [
    { name: 'Aylık Satış Raporu', date: '2023-10-15', status: 'Tamamlandı' },
    { name: 'Stok Raporu', date: '2023-10-10', status: 'Beklemede' },
    { name: 'Kullanıcı Aktivite Raporu', date: '2023-10-05', status: 'Tamamlandı' },
  ];

  const handleDeleteChip = (chipToDelete: string) => {
    setChips(chips.filter((chip) => chip !== chipToDelete));
  };

  return (
    <TebLayoutGrid container spacing="4px" columns={24}>
      <TebLayoutGrid child columns={24}>
        <TebRichHeader
          primaryTitle="Raporlar"
          infoLabel="Rapor Yönetimi"
          variant={HeaderVariant.default}
          primaryIcon="file-download"
          secondaryIcon="filter"
          onPrimaryAction={() => {}}
          onSecondaryAction={() => {}}
        />
      </TebLayoutGrid>

      <TebLayoutGrid
        child
        lg={6}
        md={6}
        sm={6}
        style={{ margin: '4px' }}
      >
        <TebCard>
          <div
            style={{
              display: 'flex',
              flexDirection: 'column',
              gap: '16px',
              marginTop: '8px',
            }}
          >
            <TebInput
              id="report-search"
              name="reportSearch"
              value={inputValue}
              type={InputType.text}
              tabIndex={0}
              placeholder="Rapor ara..."
              size={InputSize.medium}
              onInputChange={(e) => setInputValue(e.target.value)}
              icon="search"
            />

            <TebAutoComplete<AutocompleteOption>
              id="report-category"
              options={autocompleteOptions}
              value={autocompleteValue}
              inputValue={autocompleteInputValue}
              disabled={false}
              error={false}
              size={InputSize.medium}
              noOptionsText="Seçenek bulunamadı"
              placeholder="Kategori seçiniz"
              getOptionLabel={(option) => option.label}
              isOptionEqualToValue={(option, value) =>
                option.value === value.value
              }
              onChange={(event, value) => setAutocompleteValue(value)}
              onInputChange={(event, value) =>
                setAutocompleteInputValue(value)
              }
            />

            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
              {chips.map((chip, index) => (
                <TebChip
                  key={index}
                  label={chip}
                  onDelete={() => handleDeleteChip(chip)}
                  size="medium"
                />
              ))}
            </div>
          </div>
        </TebCard>
      </TebLayoutGrid>

      <TebLayoutGrid child lg={18} md={18} sm={18}>
        <TebDataGridEnterprise
          columnDefs={columnDefs}
          rowData={rowData}
          domLayout="normal"
          style={{ height: '500px', width: '100%' }}
        />
      </TebLayoutGrid>
    </TebLayoutGrid>
  );
};

export default RaporEkrani;