import React, { useState } from 'react';
import {
  TebAutoComplete,
  TebInput,
  TebDatePicker,
  TebLayoutGrid,
  TebRichHeader,
  TebCard,
  TebDataGridEnterprise,
  HeaderVariant,
  InputSize,
  InputType,
} from 'basic-ui-lib';
import type { ColDef } from 'ag-grid-community';

interface InstitutionOption {
  id: string;
  name: string;
}

const institutionOptions: InstitutionOption[] = [
  { id: '1', name: 'İstanbul Üniversitesi' },
  { id: '2', name: 'Ankara Üniversitesi' },
  { id: '3', name: 'İzmir Yüksek Teknoloji Enstitüsü' },
  { id: '4', name: 'Boğaziçi Üniversitesi' },
  { id: '5', name: 'Orta Doğu Teknik Üniversitesi' },
];

const columnDefs: ColDef[] = [
  { field: 'col1', headerName: 'col1', flex: 1 },
  { field: 'col2', headerName: 'col2', flex: 1 },
];

const rowData = [
  { col1: 'Veri 1', col2: 'Bilgi 1' },
  { col1: 'Veri 2', col2: 'Bilgi 2' },
  { col1: 'Veri 3', col2: 'Bilgi 3' },
  { col1: 'Veri 4', col2: 'Bilgi 4' },
  { col1: 'Veri 5', col2: 'Bilgi 5' },
];

const ReportScreen: React.FC = () => {
  const [institution, setInstitution] = useState<InstitutionOption | null>(null);
  const [studentNo, setStudentNo] = useState<string>('');
  const [tcNo, setTcNo] = useState<string>('');
  const [startDate, setStartDate] = useState<Date | null>(null);
  const [endDate, setEndDate] = useState<Date | null>(null);
  const [tebNo, setTebNo] = useState<string>('');

  return (
    <TebLayoutGrid container spacing="4px" columns={24}>
      <TebLayoutGrid child columns={24}>
        <TebRichHeader
          variant={HeaderVariant.filled}
          primaryTitle="TEB"
          secondaryTitle="Okul Ödeme Kontrol"
          infoLabel=""
          primaryIcon=""
          secondaryIcon=""
          onPrimaryAction={() => {
            console.log('primary action clicked');
          }}
          onSecondaryAction={() => {
            console.log('secondary action clicked');
          }}
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
              width: '100%',
              display: 'flex',
              flexDirection: 'column',
              gap: '16px',
              paddingTop: '8px',
              boxSizing: 'border-box',
            }}
          >
            <TebAutoComplete
              label="Kurum"
              options={institutionOptions}
              value={institution}
              disabled={false}
              error={false}
              size={InputSize.medium}
              noOptionsText="Sonuç bulunamadı"
              onChange={(event, value) => setInstitution(value)}
              getOptionLabel={(option) => option.name}
              isOptionEqualToValue={(option, value) =>
                option.id === value.id
              }
            />
            <TebInput
              id="student-no"
              value={studentNo}
              type={InputType.text}
              tabIndex={0}
              size={InputSize.medium}
              placeholder="Ögrenci No"
              onInputChange={(e) => setStudentNo(e.target.value)}
            />
            <TebInput
              id="tc-no"
              value={tcNo}
              type={InputType.text}
              tabIndex={0}
              size={InputSize.medium}
              placeholder="T.C.Kimlik No"
              onInputChange={(e) => setTcNo(e.target.value)}
            />
            <TebDatePicker
              value={startDate}
              label="Başlangıç Tarihi"
              onChange={(date) => setStartDate(date)}
            />
            <TebDatePicker
              value={endDate}
              label="Bitiş Tarihi"
              onChange={(date) => setEndDate(date)}
            />
            <TebInput
              id="teb-no"
              value={tebNo}
              type={InputType.text}
              tabIndex={0}
              size={InputSize.medium}
              placeholder="TEB Kayit No"
              onInputChange={(e) => setTebNo(e.target.value)}
            />
          </div>
        </TebCard>
      </TebLayoutGrid>
      <TebLayoutGrid child lg={18} md={18} sm={18}>
        <TebDataGridEnterprise
          className="ag-theme-quartz"
          columnDefs={columnDefs}
          rowData={rowData}
        />
      </TebLayoutGrid>
    </TebLayoutGrid>
  );
};

export default ReportScreen;