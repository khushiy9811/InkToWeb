import { createContext, useContext, useState, useCallback } from "react";
import client from "../api/client";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [employee, setEmployee] = useState(() => {
    const stored = localStorage.getItem("inktoweb_employee");
    return stored ? JSON.parse(stored) : null;
  });

  const applySession = useCallback((token, employeeData) => {
    localStorage.setItem("inktoweb_token", token);
    localStorage.setItem("inktoweb_employee", JSON.stringify(employeeData));
    setEmployee(employeeData);
    return employeeData;
  }, []);

  const login = useCallback(async (username, password) => {
    const res = await client.post("/api/auth/login", { username, password });
    return applySession(res.data.access_token, res.data.employee);
  }, [applySession]);

  const verifyOtp = useCallback(async (email, otp) => {
    const res = await client.post("/api/auth/verify-otp", { email, otp });
    return applySession(res.data.access_token, res.data.employee);
  }, [applySession]);

  const logout = useCallback(() => {
    localStorage.removeItem("inktoweb_token");
    localStorage.removeItem("inktoweb_employee");
    setEmployee(null);
  }, []);

  return (
    <AuthContext.Provider value={{ employee, login, verifyOtp, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
