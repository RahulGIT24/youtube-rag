import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";
import PublicRoute from "./components/PublicRoute";
import Login from "./pages/Login";
import Signup from "./pages/SignUp";
// import Signup from "./pages/Signup";
// import Home from "./pages/Home";
// import ChatInterface from "./pages/ChatInterface";

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          
          {/* Public-only Routes: Login & Signup */}
          <Route element={<PublicRoute />}>
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />
          </Route>

          {/* Protected Routes: Home & Chat */}
          <Route element={<ProtectedRoute />}>
            {/* <Route path="/" element={<Home />} /> */}
            {/* <Route path="/chat/:videoId" element={<ChatInterface />} /> */}
          </Route>

        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}