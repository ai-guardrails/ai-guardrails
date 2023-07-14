import { FC } from "react";
import { ChangeEvent } from "react";
import { IconUpload } from "@tabler/icons-react";
import { Message } from "@/types/chat";

interface Props {
  inputs: string[];
  handleSend: Function;
}

const AdditionalInputs: FC<Props> = ({ inputs, handleSend }) => {
  const handleDocumentUpload = async (
    event: ChangeEvent<HTMLInputElement>
  ) => {
    const files = event.target.files;
    if (!files || files.length === 0) {
      return;
    }

    const formData = new FormData(); 
    formData.append("files", files[0]);
    
    let message: Message = {
      role: "user",
      content: `Summarize ${files[0].name}`,
      userActionRequired: false,
      msg_info: null
    }
    handleSend(message,0,false,formData);
  };

  return (
    <>
      {inputs.map((input, index) => {
        if (input == "fileUpload") {
          return (
              <label  key={index} className="flex gap-1 items-center w-32 p-2.5 rounded-md bg-[black] hover:bg-[#595959]  dark:bg-[#202123] dark:hover:bg-[#3e3f40] cursor-pointer">
                <IconUpload />
                Upload File
                <input
                  type="file"
                  accept=".pdf "
                  hidden
                  onChange={handleDocumentUpload}
                />
              </label>

          );
        }
      })}
    </>
  );
};
export default AdditionalInputs;
