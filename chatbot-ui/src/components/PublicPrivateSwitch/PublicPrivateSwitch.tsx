import { FC, useState, useContext } from "react";
import HomeContext from "@/pages/home/home.context";
import { styled } from "@mui/material/styles";
import Switch, { SwitchProps } from "@mui/material/Switch";

import { IconLock, IconLockOpen } from "@tabler/icons-react";
import IconButton from "@mui/material/IconButton";
import Tooltip from "@mui/material/Tooltip";

interface Props {
  size: string | number | undefined;
}

const CustomSwitch = styled((props: SwitchProps) => (
  <Switch
    focusVisibleClassName=".Mui-focusVisible"
    disableRipple
    {...props}
    disabled
  />
))(({ theme }) => ({
  width: 42,
  height: 26,
  padding: 0,
  "& .MuiSwitch-switchBase": {
    padding: 0,
    margin: 2,
    transitionDuration: "300ms",
    "&.Mui-checked": {
      transform: "translateX(16px)",
      color: "#fff",
      "& + .MuiSwitch-track": {
        backgroundColor: theme.palette.mode === "dark" ? "#2ECA45" : "#65C466",
        opacity: 1,
        border: 0,
      },
      "&.Mui-disabled + .MuiSwitch-track": {
        opacity: 0.5,
      },
    },
    "&.Mui-focusVisible .MuiSwitch-thumb": {
      color: "#65c466",
      border: "6px solid #fff",
    },
    "&.Mui-disabled .MuiSwitch-thumb": {
      color:
        theme.palette.mode === "light"
          ? theme.palette.grey[100]
          : theme.palette.grey[600],
    },
    "&.Mui-disabled + .MuiSwitch-track": {
      opacity: theme.palette.mode === "light" ? 0.7 : 0.3,
    },
  },
  "& .MuiSwitch-thumb": {
    boxSizing: "border-box",
    width: 22,
    height: 22,
  },
  "& .MuiSwitch-track": {
    borderRadius: 26 / 2,
    backgroundColor: theme.palette.mode === "light" ? "#E9E9EA" : "#39393D",
    opacity: 1,
    transition: theme.transitions.create(["background-color"], {
      duration: 500,
    }),
  },
}));

const PublicPrivateSwitch: FC<Props> = ({ size }) => {
  const {
    state: { isPrivate },
    handleIsPrivate,
  } = useContext(HomeContext);

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    handleIsPrivate(event.target.checked);
  };
  return (
    <>
      <div className="flex justify-around  items-center pb-2 pt-4 text-sm text-black dark:text-gray-400">
        <div className="flex flex-col justify-around  items-center">
          <IconLockOpen size={size} />
          Public LLM
        </div>
        <Tooltip title="Feature disabled. It will be available soon.">
          <IconButton>
            <CustomSwitch
              sx={{ m: 1 }}
              checked={isPrivate}
              onChange={handleChange}
            />
          </IconButton>
        </Tooltip>

        <div className="flex flex-col justify-around  items-center text-black dark:text-gray-400">
          <IconLock size={size} />
          Private LLM
        </div>
      </div>
    </>
  );
};
export default PublicPrivateSwitch;
