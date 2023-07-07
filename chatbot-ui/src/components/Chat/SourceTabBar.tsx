import Box from "@mui/material/Box";
import Tab from "@mui/material/Tab";
import TabContext from "@mui/lab/TabContext";
import TabList from "@mui/lab/TabList";
import TabPanel from "@mui/lab/TabPanel";
import { FC, useState } from "react";
import { AssistantMessage } from "./ChatMessage";

export interface TabsProps {
  sources: [];
}

export const SourceTabBar: FC<TabsProps> = ({ sources }) => {
  const [value, setValue] = useState("0");

  const handleChange = (event: React.SyntheticEvent, newValue: string) => {
    setValue(newValue);
  };

  const style = {
    padding: "1.5em 0px 0px 0px",
    fontFamily: "'Inter', sans-serif",
    fontWeight: 500,
  };
  return (
    <Box sx={{ width: "100%", typography: "body1" }}>
      <TabContext value={value}>
        <Box
          sx={{
            borderBottom: 1,
            borderColor: "divider",
            color: "white",
          }}
        >
          <TabList
            onChange={handleChange}
            aria-label="lab API tabs example"
            sx={{
              "& .MuiTab-root": {
                fontFamily: "'Inter', sans-serif", // Set the font-family
                fontWeight: 600,
                color: "white",
                textTransform: "Capitalize",
                paddingTop: "0px",
              },
              "& .MuiButtonBase-root.Mui-selected": {
                color: "white",
              },
              "& .MuiTabs-indicator": {
                backgroundColor: "white",
                marginBottom: "8px",
              },
              "& .MuiTabs-scroller": {
                overflowX: "scroll !important",
                "&::-webkit-scrollbar": {
                  height: "0.4em",
                },
                "&::-webkit-scrollbar-thumb": {
                  backgroundColor: "#7e7e7e", // Change this to your desired color
                },
                "&::-webkit-scrollbar-thumb:hover": {
                  backgroundColor: "#fff", // Change this to your desired color
                },
                "&::-webkit-scrollbar-track": {
                  backgroundColor: "#343541", // Change this to your desired color
                },
              },
            }}
          >
            {sources.map((source: any, index: number) => {
              return (
                <Tab
                  label={source.fileName}
                  value={`${index}`}
                  key={index}
                ></Tab>
              );
            })}
          </TabList>
        </Box>
        {sources.map((source: any, index: number) => {
          return (
            <TabPanel value={`${index}`} sx={style} key={index}>
              <AssistantMessage content={source.doc} />
            </TabPanel>
          );
        })}
      </TabContext>
    </Box>
  );
};
