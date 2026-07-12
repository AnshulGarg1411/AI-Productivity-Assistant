import { useEffect, useRef } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import toast from "react-hot-toast";
import { useAuth } from "../contexts/AuthContext";

// The backend redirects here as: /oauth/callback?token=<jwt>
const OAuthCallback = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { login } = useAuth();
  const hasRun = useRef(false);

  useEffect(() => {
    if (hasRun.current) return;
    hasRun.current = true;

    const token = searchParams.get("token");

    if (!token) {
      toast.error("Login failed. Please try again.");
      navigate("/login", { replace: true });
      return;
    }

    login(token)
      .then(() => {
        toast.success("Signed in successfully");
        navigate("/dashboard", { replace: true });
      })
      .catch(() => {
        toast.error("Login failed. Please try again.");
        navigate("/login", { replace: true });
      });
  }, [searchParams, login, navigate]);

  return (
    <div className="flex justify-center items-center h-screen">
      <h1 className="text-2xl font-semibold text-gray-600">Signing you in...</h1>
    </div>
  );
};

export default OAuthCallback;
