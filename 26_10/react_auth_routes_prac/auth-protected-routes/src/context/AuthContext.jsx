import { createContext, useContext, useState } from "react";
 
const AuthContext = createContext();
 
export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const savedUser = sessionStorage.getItem("user");
    return savedUser ? JSON.parse(savedUser) : null;
  });
 
  function login(email, password) {
    // Mock credentials for this lesson only
    if (email === "admin@example.com" && password === "123456") {
      const loggedInUser = { email };
      sessionStorage.setItem("user", JSON.stringify(loggedInUser));
      setUser(loggedInUser);
      return true;
    }
 
    return false;
  }
 
  function logout() {
    sessionStorage.removeItem("user");
    setUser(null);
  }
 
  return (
<AuthContext.Provider value={{ user, login, logout }}>
      {children}
</AuthContext.Provider>
  );
}
 
export function useAuth() {
  return useContext(AuthContext);
}
