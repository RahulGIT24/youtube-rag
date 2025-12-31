import { useEffect, useState } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { CheckCircle, XCircle, Loader2 } from "lucide-react";
import toast from "react-hot-toast";
import api from "../lib/api";

export default function Verify() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const token = searchParams.get("token");

  const [status, setStatus] = useState<"loading" | "success" | "error">("loading");
  const [message, setMessage] = useState("Verifying your account...");
  const [countdown, setCountdown] = useState(5);

  useEffect(() => {
    if (!token) {
      setStatus("error");
      setMessage("Invalid or missing verification token.");
      startRedirect("/signup");
      return;
    }

    const verifyAccount = async () => {
      try {
        const res = await api.get(`/auth/verify-account?token=${token}`);
        
        setStatus("success");
        setMessage(res.data.message || "Account verified successfully!");
        toast.success(res.data.message);
        startRedirect("/login");
      } catch (err: any) {
        setStatus("error");
        const errMsg = err.response?.data?.detail || "Verification failed or token expired.";
        setMessage(errMsg);
        toast.error(errMsg);
        startRedirect("/signup");
      }
    };

    verifyAccount();
  }, [token]);

  const startRedirect = (path: string) => {
    const timer = setInterval(() => {
      setCountdown((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          navigate(path);
        }
        return prev - 1;
      });
    }, 1000);
  };

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="w-full max-w-md rounded-2xl bg-white p-8 text-center shadow-xl border border-gray-100">
        
        {/* Loading State */}
        {status === "loading" && (
          <div className="flex flex-col items-center">
            <Loader2 className="h-16 w-16 animate-spin text-indigo-600" />
            <h2 className="mt-6 text-2xl font-bold text-gray-800">Checking Token</h2>
          </div>
        )}

        {/* Success State */}
        {status === "success" && (
          <div className="flex flex-col items-center">
            <CheckCircle className="h-16 w-16 text-green-500" />
            <h2 className="mt-6 text-2xl font-bold text-gray-900">Verified!</h2>
          </div>
        )}

        {/* Error State */}
        {status === "error" && (
          <div className="flex flex-col items-center">
            <XCircle className="h-16 w-16 text-red-500" />
            <h2 className="mt-6 text-2xl font-bold text-gray-900">Verification Failed</h2>
          </div>
        )}

        <p className="mt-4 text-gray-600">{message}</p>

        <div className="mt-8 border-t border-gray-100 pt-6">
          <p className="text-sm text-gray-500">
            Redirecting you in <span className="font-bold text-indigo-600">{countdown}</span> seconds...
          </p>
          <button
            onClick={() => navigate(status === "success" ? "/login" : "/signup")}
            className="mt-4 text-sm font-medium text-indigo-600 hover:text-indigo-500"
          >
            Click here if you aren't redirected
          </button>
        </div>
      </div>
    </div>
  );
}