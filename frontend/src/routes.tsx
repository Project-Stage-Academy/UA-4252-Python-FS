import { Navigate } from "react-router-dom";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Register from "./pages/Register";
import StartupView from "./pages/StartupView";
import InvestorDashboard from "./pages/InvestorDashboard";
import Inbox from "./pages/Inbox";
import RegisterStartup from "./pages/RegisterStartup";
import RegisterInvestor from "./pages/RegisterInvestor";
import PasswordResetRequest from "./pages/PasswordResetRequest";
import PasswordResetConfirm from "./pages/PasswordResetConfirm";
import RestorePassword from "./pages/RestorePassword";
import VerifyEmail from "./pages/VerifyEmail";
import ErrorPage from "./pages/ErrorPage";

export const routes = [
  { path: "/", element: <Home /> },
  { path: "/login", element: <Login /> },
  { path: "/register", element: <Register /> },
  { path: "/register-startup", element: <RegisterStartup /> },
  { path: "/register-investor", element: <RegisterInvestor /> },
  { path: "/startups/:id", element: <StartupView /> },
  { path: "/dashboard", element: <InvestorDashboard /> },
  { path: "/messages", element: <Inbox /> },
  { path: "/forgot-password", element: <PasswordResetRequest /> },
  { path: "/verify-email", element: <VerifyEmail /> },
  { path: "/restore-password", element: <RestorePassword /> },
  { path: "/reset-password", element: <PasswordResetConfirm /> },
  { path: "/error", element: <ErrorPage /> },
  { path: "*", element: <Navigate to="/error" replace /> }
];
