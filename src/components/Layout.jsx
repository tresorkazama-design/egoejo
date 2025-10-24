import "../styles/header.css";
import { Outlet, NavLink } from "react-router-dom";

export default function Layout(){
  return (
    <div style={{minHeight:"100dvh", background:"#060b0a", color:"#dffdf5"}}>
      <header className="app-header" style={{display:"flex", gap:24, alignItems:"center", padding:"12px 20px"}}>
        <NavLink to="/" style={{textDecoration:"none", color:"#74ffd7", fontWeight:700}}>EGOEJO</NavLink>
        <nav style={{display:"flex", gap:16}}>
          <NavLink to="/univers">Univers</NavLink>
        </nav>
      </header>
      <main>
        <Outlet />
      </main>
    </div>
  );
}

