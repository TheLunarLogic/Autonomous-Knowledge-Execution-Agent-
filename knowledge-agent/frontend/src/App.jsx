import { BrowserRouter, Routes, Route, NavLink } from "react-router-dom";
import Home from "./pages/Home";
import Logs from "./pages/Logs";
import "./index.css";

export default function App() {
  return (
    <BrowserRouter>
      <div className="app">
        {/* Navigation */}
        <nav className="nav-bar">
          <div className="nav-brand">
            <span className="nav-icon">🧠</span>
            <span className="nav-title">AKEA</span>
          </div>
          <div className="nav-links">
            <NavLink to="/" end className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
              Agent
            </NavLink>
            <NavLink to="/logs" className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
              Audit Logs
            </NavLink>
          </div>
        </nav>

        {/* Content */}
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/logs" element={<Logs />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
