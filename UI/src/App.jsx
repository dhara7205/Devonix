// src/App.jsx
import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import ProtectedRoute from "./components/ProtectedRoute";
import Header from "./components/Header";
import Home from "./pages/Home";
import Embed from "./pages/Embed";
import Query from "./pages/Query";
import Settings from "./pages/Settings";
import LoginSelection from "./pages/LoginSelection";
import PersonalLogin from "./pages/PersonalLogin";
import EnterpriseLogin from "./pages/EnterpriseLogin";
import Profile from "./pages/Profile";
import NotFound from "./pages/NotFound"; // make sure this exists

export default function App() {
  return (
    <BrowserRouter>
      <Header />
      <Routes>
        <Route path="/" element={<Home />} />

        <Route path="/login" element={<LoginSelection />} />
        <Route path="/login/personal" element={<PersonalLogin />} />
        <Route path="/login/enterprise" element={<EnterpriseLogin />} />
        <Route path="/Profile" element={<Profile/>}/>

        <Route element={<ProtectedRoute />}>
          <Route path="/embed" element={<Embed />} />
          <Route path="/query" element={<Query />} />
          <Route path="/settings" element={<Settings />} />
        </Route>

        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  );
}
