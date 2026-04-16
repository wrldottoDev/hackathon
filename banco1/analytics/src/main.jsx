import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import "@xyflow/react/dist/style.css";
import App from "./App";
import { AnalysisAuthProvider } from "./auth";
import "./styles.css";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <BrowserRouter>
      <AnalysisAuthProvider>
        <App />
      </AnalysisAuthProvider>
    </BrowserRouter>
  </React.StrictMode>,
);
