import {
  AppBar,
  Chip,
  Divider,
  IconButton,
  Toolbar,
  Typography,
} from "@mui/material";

import SvgPodiumLogo from "./SvgPodiumLogo";

export const Header = () => {
  return (
    <AppBar
      position="static"
      sx={{
        backgroundImage:
          "linear-gradient(270.35deg, #FFFFFF 73.58%, #D9F5FC 104.58%)",
      }}
    >
      <Toolbar sx={{display:"flex",justifyContent:"center"}}>
        <SvgPodiumLogo style={{ height: '36px', width: '36px', marginLeft: '10px',marginRight:'10px' }}/>
        <Typography
          variant="h6"
          noWrap
          component="div"
          sx={{ fontSize: "15px", marginRight: "5px" ,color:"#18B4EA" }}
        >
          Podium
        </Typography>
        <Typography
          variant="h6"
          noWrap
          component="div"
          sx={{ fontSize: "16px", color: "#75777A", fontWeight: "600" }}
        >
          {"Ai Gaurdrails"}
        </Typography>
        <Typography variant="subtitle2" component="span">
          <Chip
            label="Beta"
            variant="outlined"
            size="small"
            style={{
              borderColor: "#F86F03",
              color: "#F86F03",
              marginLeft: "5px",
              marginRight: "5px",
            }}
          />
        </Typography>
      </Toolbar>
    </AppBar>
  );
};
