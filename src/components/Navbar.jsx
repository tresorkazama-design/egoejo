import React from 'react';
import { Link } from 'react-router-dom';

const Navbar = () => {
  return (
    <nav style={{ 
      backgroundColor: 'rgba(0,0,0,0.8)', // Noir semi-transparent pour l'effet "Dark Glass"
      backdropFilter: 'blur(5px)', // Effet de verre (inspirÃƒÂ© Noomo Labs)
      color: '#F0F0F0',
      padding: '18px 50px',
      position: 'fixed', 
      top: 0, 
      width: '100%', 
      zIndex: 1000,
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
    }}>
      <Link to="/" style={{ textDecoration: 'none', color: '#ffc300', fontSize: '1.8em', fontWeight: 'bold' }}>
        EGOEJO
      </Link>
      <div style={{ display: 'flex', gap: '35px' }}>
        <Link to="/vision" style={{ textDecoration: 'none', color: '#67ff9b', fontSize: '1.1em', fontWeight: 500 }}>
          VISION
        </Link>
        <Link to="/about" style={{ textDecoration: 'none', color: '#F0F0F0', fontSize: '1.1em', fontWeight: 500 }}>
          HÃƒâ€°RITAGE
        </Link>
        <Link to="/projets" style={{ textDecoration: 'none', color: '#ffc300', fontSize: '1.1em', fontWeight: 500 }}>
          IMPACT
        </Link>
      </div>
    </nav>
  );
};
export default Navbar;