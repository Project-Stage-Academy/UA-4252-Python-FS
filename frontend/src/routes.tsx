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

export const routes = [
  { path: "/", element: <Home /> },
  { path: "/login", element: <Login /> },
  { path: "/register", element: <Register /> },
  { path: "/register-startup", element: <RegisterStartup /> },
  { path: "/register-investor", element:<RegisterInvestor />},
  { path: "/startups/:id", element: <StartupView /> },
  { path: "/dashboard", element: <InvestorDashboard /> },
  { path: "/messages", element: <Inbox /> },
  { path: "/forgot-password", element: <PasswordResetRequest /> },
  { path: "/reset-password", element: <PasswordResetConfirm /> },
  { path: "*", element: <div>404 Not Found</div> }
];
