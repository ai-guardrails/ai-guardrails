import { ChangeEvent, useState } from "react";
import { Button } from "@mui/material";
import { CustomDataGrid } from "./CustomDataGrid";
import { IconUpload } from '@tabler/icons-react';
import { uploadDocuments ,deleteDocsGridData} from "@/services/DocsService";
import toast from "react-hot-toast";

export const PrivateDocuments = () => {
  const [ refereshGridData, setRefereshGridData ] = useState<boolean>(true)

  const handleDocumentsUpload = async (
    event: ChangeEvent<HTMLInputElement>
  ) => {
    const files = event.target.files;
    if (!files || files.length === 0) {
      return;
    }

    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
      formData.append("files", files[i]);
    }

    toast.promise(
      uploadDocuments(formData), //calling api here
      {
        loading: `Uploading ${files.length} Documents`,
        success: <b>Documents Uploaded</b>,
        error: <b>Error in Uploading Documents</b>,
      },
      {
        position: "bottom-center",
      })
      .then(()=>{
        setRefereshGridData(!refereshGridData);
        event.target.value = "";
      })
  };

  function handleDelete(id:any) {
    // Handle delete logic here
    toast.promise(
      deleteDocsGridData(id), //calling api here
      {
        loading: `Deleting Document`,
        success: <b>Documents Deleted</b>,
        error: <b>Error in Deleting Documents</b>,
      },
      {
        position: "bottom-center",
      })
      .then(()=>{
        setRefereshGridData(!refereshGridData);
      })
    
  }
  const columns = [
    { field: "title", headerName: "Title", flex: 5 },
    { 
      field: 'actions', 
      headerName: 'Actions', 
      width: 100,
      renderCell: (params:any) => (
        <Button
          variant="outlined"
          size="small"
          sx={{ backgroundColor: '#ba071f', color: 'white', fontSize: '12px' 
          ,padding: '3px',textTransform: 'Capitalize', borderColor: '#ba071f'}}
          onClick={() => handleDelete(params.row.id)}
        >
          Delete
        </Button>
      ),
    },
  ];
  const entity = "documents";
  const initialSort = [
    {
      field: "title",
      sort: "asc",
    },
  ];
  return (
    <>
      <div
        style={{
          display: "flex",
          justifyContent: "flex-end",
          margin: "25px 40px",
          marginBottom: "0px",
        }}
      >
        <Button
          variant="contained"
          component="label"
          startIcon={<IconUpload />}
        >
          Upload Documents
          <input
            type="file"
            multiple
            accept=".doc, .docx, .pdf"
            hidden
            onChange={handleDocumentsUpload}
          />
        </Button>
      </div>
      <CustomDataGrid
        columns={columns}
        entity={entity}
        initialSort={initialSort}
        refereshGridData={refereshGridData}
      />
    </>
  );
};
