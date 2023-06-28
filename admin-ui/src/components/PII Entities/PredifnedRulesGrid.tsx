import React, { useState } from "react";
import { CustomDataGrid } from "../DataGrids/CustomDataGrid";
import Switch from '@mui/material/Switch';
import { updateGridData } from "@/services";
import toast from "react-hot-toast";

interface Row {
  id: string;
  is_active: boolean;
  name: string;
  criticality: string;
}

export const PredefinedRulesGrid = () => {
  const [switchStates, setSwitchStates] = useState<{ [id: string]: boolean }>({});

  const handleGridDataUpdate = (updatedData: Row[]) => {
    const updatedStates: { [id: string]: boolean } = {};
    updatedData.forEach((row) => {
      updatedStates[row.id] = row.is_active;
    });
    setSwitchStates(updatedStates);
  };

  const handleButtonClick = async (id: string, is_active: boolean) => {
    const updatedStates = { ...switchStates };
    updatedStates[id] = !updatedStates[id];
    try{
      const response = await updateGridData('predefined_rules', id, { is_active: updatedStates[id] });
      setSwitchStates(updatedStates);
    }
    catch(error:any){
      console.log(error);
      toast.error(error?.message,{
        duration:3000,
        position:"bottom-center"
      })
    }
  };

  const columns = [
    { field: 'name', headerName: 'Name', flex: 3 },
    { field: 'criticality', headerName: 'Criticality', flex: 3 },
    {
      field: 'is_active',
      headerName: 'Active',
      width: 200,
      renderCell: (params: any) => (
        <Switch
          checked={switchStates[params.row.id] || false}
          onChange={() => handleButtonClick(params.row.id, params.row.is_active)}
          inputProps={{ 'aria-label': 'controlled' }}
        />
      ),
    },
  ];

  const entity = 'predefined_rules';

  const initialSort = [
    {
      field: "name",
      sort: "asc",
    },
  ];

  return (
    <CustomDataGrid columns={columns} entity={entity} initialSort={initialSort} onGridDataUpdate={handleGridDataUpdate} />
  );
};
