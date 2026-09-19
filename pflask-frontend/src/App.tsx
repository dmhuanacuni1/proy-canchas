import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import CanchasPage from './pages/CanchasPage';
import MisReservasPage from './pages/MisReservasPage';
import ReservaFormPage from './pages/ReservaFormPage';

function App() {
  return (
    <BrowserRouter>
      <nav style={{ padding: '10px', background: '#eee' }}>
        <Link to="/" style={{ marginRight: '10px' }}>Canchas</Link>
        <Link to="/mis-reservas">Mis Reservas</Link>
      </nav>
      <Routes>
        <Route path="/" element={<CanchasPage />} />
        <Route path="/reservar/:idCancha" element={<ReservaFormPage />} />
        <Route path="/mis-reservas" element={<MisReservasPage />} />
      </Routes>
    </BrowserRouter>
  );
}
export default App;