import Home from "./pages/Home";
import Login from "./pages/Login";
import Register from "./pages/Register";
import StartupView from "./pages/StartupView";
import InvestorDashboard from "./pages/InvestorDashboard";
import Inbox from "./pages/Inbox";
import RegisterStartup from "./pages/RegisterStartup";

export const routes = [
  { path: "/", element: <Home /> },
  { path: "/login", element: <Login /> },
  { path: "/register", element: <Register /> },
  { path: "/registerstartup", element: <RegisterStartup /> },
  { path: "/startups/:id", element: <StartupView /> },
  { path: "/dashboard", element: <InvestorDashboard /> },
  { path: "/messages", element: <Inbox /> },
  { path: "*", element: <div>404 Not Found</div> },
];
