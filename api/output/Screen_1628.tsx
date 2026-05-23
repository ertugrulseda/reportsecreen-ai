import React, { useState } from 'react';
import { TebInput, TebAutoComplete, TebChip, TebRichHeader, TebCard, TebDataGridEnterprise, TebLayoutGrid, InputSize, InputType, HeaderVariant } from 'basic-ui-lib';
import { ColDef } from 'ag-grid-community';

interface ReportData {
  id: number;
  name: string;
  status: string;
  date: string;
}

const ReportScreen: React.FC = () => {
  const [inputValue, setInputValue] = useState<string>('');
  const [autocompleteValue, setAutocompleteValue] = useState<string | null>(null);
  const [autocompleteInputValue, setAutocompleteInputValue] = useState<string>('');
  const [chips, setChips] = useState<string[]>(['Status: Active', 'Type: Monthly']);

  const autocompleteOptions = [
    'Active Reports',
    'Pending Reports',
    'Completed Reports',
    'All Reports'
  ];

  const gridData: ReportData[] = [
    { id: 1, name: 'Monthly Sales Report', status: 'Completed', date: '2023-05-15' },
    { id: 2, name: 'Quarterly Financial Report', status: 'Pending', date: '2023-05-10' },
    { id: 3, name: 'User Activity Report', status: 'Active', date: '2023-05-05' },
  ];

  const columnDefs: ColDef<ReportData>[] = [
    { headerName: 'ID', field: 'id', flex: 1 },
    { headerName: 'Report Name', field: 'name', flex: 1 },
    { headerName: 'Status', field: 'status', flex: 1 },
    { headerName: 'Date', field: 'date', flex: 1 },
  ];

  const handleAddChip = () => {
    if (autocompleteValue) {
      setChips([...chips, autocompleteValue]);
      setAutocompleteValue(null);
      setAutocompleteInputValue('');
    }
  };

  const handleDeleteChip = (chipToDelete: string) => {
    setChips(chips.filter(chip => chip !== chipToDelete));
  };

  return (
    <TebLayoutGrid container spacing="4px" columns={24}>
      <TebLayoutGrid child columns={24}>
        <TebRichHeader
          primaryTitle="Report Screen"
          infoLabel="View and manage reports"
          variant={HeaderVariant.default}
          primaryIcon="file"
          secondaryIcon="settings"
          onPrimaryAction={() => {}}
          onSecondaryAction={() => {}}
        />
      </TebLayoutGrid>
      
      <TebLayoutGrid child lg={6} md={6} sm={6} style={{ margin: '4px' }}>
        <TebCard>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', marginTop: '8px' }}>
            <TebInput
              id="report-search"
              name="reportSearch"
              value={inputValue}
              type={InputType.text}
              tabIndex={0}
              placeholder="Search reports..."
              size={InputSize.medium}
              onInputChange={(e) => setInputValue(e.target.value)}
              width="100%"
            />
            
            <TebAutoComplete
              id="report-filter"
              options={autocompleteOptions}
              value={autocompleteValue}
              inputValue={autocompleteInputValue}
              disabled={false}
              placeholder="Select report filter"
              error={false}
              size={InputSize.medium}
              width="100%"
              noOptionsText="No filters available"
              tabIndex={0}
              getOptionLabel={(option) => option}
              onChange={(event, value) => setAutocompleteValue(value)}
              onInputChange={(event, value) => setAutocompleteInputValue(value)}
            />
            
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
              {chips.map((chip, index) => (
                <TebChip
                  key={index}
                  label={chip}
                  onDelete={() => handleDeleteChip(chip)}
                  size="small"
                />
              ))}
            </div>
          </div>
        </TebCard>
      </TebLayoutGrid>
      
      <TebLayoutGrid child lg={18} md={18} sm={18}>
        <TebDataGridEnterprise
          columnDefs={columnDefs}
          rowData={gridData}
          domLayout="normal"
          style={{ width: '100%', height: '500px' }}
        />
      </TebLayoutGrid>
    </TebLayoutGrid>
  );
};

export default ReportScreen;