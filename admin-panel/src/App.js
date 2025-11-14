import React from 'react';

// Composant de remplacement pour le site public
const HomePage = () => (
  <div className="text-center p-12 min-h-screen flex items-center justify-center bg-gray-100">
    <div className="bg-white p-10 rounded-xl shadow-2xl">
      <h1 className="text-5xl font-extrabold text-green-700">Bienvenue sur EGOEJO</h1>
      <p className="mt-4 text-xl text-gray-600">Site Public OK - Construction React réussie !</p>
    </div>
  </div>
);

function App() {
  return (
    <HomePage />
  );
}

export default App;