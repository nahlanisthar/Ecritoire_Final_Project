import { createTheme } from "@mui/material/styles";

const darkTheme = createTheme({
  palette: {
    mode: "dark",
    primary: {
      main: "#FFD700", 
    },
    secondary: {
      main: "#90caf9",
    },
    background: {
      default: "#121212",
      paper: "#000000",
    },
    text: {
      primary: "#ffffff",
      secondary: "#d3d3d3ff",
    },
  },
  typography: {
    fontFamily: '"Sansita", sans-serif',
  },
});

export default darkTheme;
