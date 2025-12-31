import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function PublicRoute() {
  const { user, loading } = useAuth();

  if (loading) return null; // Or a small spinner

  return !user ? <Outlet /> : <Navigate to="/" replace />;
}