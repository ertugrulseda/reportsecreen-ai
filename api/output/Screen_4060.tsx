import React, { useState } from 'react';
import {
  TebInput,
  TebAutoComplete,
  TebCheckBox,
  TebButton,
  TebRichHeader,
  TebCard,
  TebDataGridEnterprise,
  TebLayoutGrid,
  InputSize,
  InputType,
  ButtonVariant,
  ButtonType,
  HeaderVariant,
} from 'basic-ui-lib';
import { ColDef } from 'ag-grid-community';

interface AutocompleteOption {
  label: string;
  value: string;
}

const ReportScreen: React.FC = () => {
  // State for inputs
  const [input1Value, setInput1Value] = useState('');
  const [input2Value, setInput2Value] = useState('');
  const [input3Value, setInput3Value] = useState('');
  const [autocompleteValue, setAutocompleteValue] =
    useState<AutocompleteOption | null>(null);
  const [checkbox1Value, setCheckbox1Value] = useState(false);
  const [checkbox2Value, setCheckbox2Value] = useState(false);

  // Autocomplete options
  const autocompleteOptions: AutocompleteOption[] = [
    { label: 'Option 1', value: '1' },
    { label: 'Option 2', value: '2' },
    { label: 'Option 3', value: '3' },
  ];

  // Data grid column definitions
  const columnDefs: ColDef[] = [
    { headerName: 'ID', field: 'id', flex: 1 },
    { headerName: 'Name', field: 'name', flex: 1 },
    { headerName: 'Status', field: 'status', flex: 1 },
  ];

  // Data grid row data
  const rowData = [
    { id: '1', name: 'Report 1', status: 'Completed' },
    { id: '2', name: 'Report 2', status: 'Pending' },
    { id: '3', name: 'Report 3', status: 'Failed' },
  ];

  return (
    <TebLayoutGrid container spacing="4px" columns={24}>
      <TebLayoutGrid child columns={24}>
        <TebRichHeader
          primaryTitle="Raporlar"
          infoLabel="Rapor yönetimi"
          variant={HeaderVariant.default}
          primaryIcon="file"
          secondaryIcon="help"
          onPrimaryAction={() => {}}
          onSecondaryAction={() => {}}
        />
      </TebLayoutGrid>

      <TebLayoutGrid
        child
        lg={6}
        md={6}
        sm={6}
        style={{ margin: '4px', height: 'fit-content' }}
      >
        <TebCard title="Filtreler">
          <div
            style={{
              display: 'flex',
              flexDirection: 'column',
              gap: '16px',
              marginTop: '8px',
            }}
          >
            <TebInput
              id="input1"
              name="input1"
              value={input1Value}
              type={InputType.text}
              tabIndex={0}
              placeholder="Input 1"
              size={InputSize.medium}
              onInputChange={(e) => setInput1Value(e.target.value)}
            />

            <TebInput
              id="input2"
              name="input2"
              value={input2Value}
              type={InputType.text}
              tabIndex={0}
              placeholder="Input 2"
              size={InputSize.medium}
              onInputChange={(e) => setInput2Value(e.target.value)}
            />

            <TebAutoComplete
              id="autocomplete"
              options={autocompleteOptions}
              value={autocompleteValue}
              disabled={false}
              error={false}
              size={InputSize.medium}
              noOptionsText="Seçenek bulunamadı"
              placeholder="Select option"
              getOptionLabel={(option) => option.label}
              isOptionEqualToValue={(option, value) =>
                option.value === value.value
              }
              onChange={(event, value) => setAutocompleteValue(value)}
            />

            <TebCheckBox
              id="checkbox1"
              checked={checkbox1Value}
              onChange={(e) => setCheckbox1Value(e.target.checked)}
              label="Checkbox 1"
            />

            <TebCheckBox
              id="checkbox2"
              checked={checkbox2Value}
              onChange={(e) => setCheckbox2Value(e.target.checked)}
              label="Checkbox 2"
            />

            <TebInput
              id="input3"
              name="input3"
              value={input3Value}
              type={InputType.text}
              tabIndex={0}
              placeholder="Input 3"
              size={InputSize.medium}
              onInputChange={(e) => setInput3Value(e.target.value)}
            />

            <div style={{ display: 'flex', gap: '8px' }}>
              <TebButton
                size={InputSize.medium}
                variant={ButtonVariant.primary}
                type={ButtonType.button}
                onClick={() => {}}
              >
                Uygula
              </TebButton>
              <TebButton
                size={InputSize.medium}
                variant={ButtonVariant.secondary}
                type={ButtonType.button}
                onClick={() => {}}
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
          style={{ height: '500px', width: '100%' }}
        />
      </TebLayoutGrid>
    </TebLayoutGrid>
  );
};

export default ReportScreen;