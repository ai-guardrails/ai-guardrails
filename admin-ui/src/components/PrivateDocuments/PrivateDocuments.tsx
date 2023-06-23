import { ChangeEvent, useState } from "react";
import { Button } from "@mui/material";
import { CustomDataGrid } from "../DataGrids/CustomDataGrid";
import UploadOutlinedIcon from "@mui/icons-material/UploadOutlined";
import { uploadDocuments } from "@/services";
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
      }
    ).then(()=>{
      setRefereshGridData(!refereshGridData);
      event.target.value = "";
    })
  };

  const columns = [
    { field: "title", headerName: "Title", flex: 5 },
    { field: "description", headerName: "Description", flex: 5 },
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
          startIcon={<UploadOutlinedIcon />}
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
