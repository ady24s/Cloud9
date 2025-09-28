import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

const AuthSuccess = () => {
  const navigate = useNavigate();

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const token = params.get("token");
    if (token) {
      localStorage.setItem("access_token", token);
      navigate("/choose-cloud");
    } else {
      navigate("/");
    }
  }, [navigate]);

  return <p>Signing you in...</p>;
};

export default AuthSuccess;
