import logo from "./logo.svg";
import "./App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import AppHeader from "./components/AppHeader";
import YourVn from "./pages/YourVn";
import { Layout } from "antd";
import OrDemo from "./pages/OrDemo";
import FakeData from "./pages/FakeData";
import ShowCases from "./pages/ShowCases";

function App() {
  return (
    <Layout>
      <BrowserRouter>
        <AppHeader />
        <Routes>
          <Route path="/" element={<YourVn />} />
          <Route path="/or101" element={<OrDemo />} />
          <Route path="/fakedata" element={<FakeData />} />
          <Route path="/showcases" element={<ShowCases />} />
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </BrowserRouter>
    </Layout>
  );
}

export default App;
