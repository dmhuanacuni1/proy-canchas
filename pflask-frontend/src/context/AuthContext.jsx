import { createContext, useState, useContext } from 'react';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  // SOLUCIÓN: Leemos el localStorage directamente desde el inicio (Lazy initialization)
  const [user, setUser] = useState(() => {
    const token = localStorage.getItem('token');
    const role = localStorage.getItem('role');
    
    // Si encuentra datos guardados, los carga al instante. Si no, inicia en null.
    if (token && role) {
      return { token, role };
    }
    return null;
  });

  const login = (userData) => {
    localStorage.setItem('token', userData.token);
    localStorage.setItem('role', userData.role);
    setUser(userData);
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);