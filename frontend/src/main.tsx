import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'

import Home from './pages/Home'
import Login from './pages/Login'
import Register from './pages/Register'
import StartupView from './pages/StartupView'
import InvestorDashboard from './pages/InvestorDashboard'
import Inbox from './pages/Inbox'

ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/startups/:id" element={<StartupView />} />
        <Route path="/dashboard" element={<InvestorDashboard />} />
        <Route path="/messages" element={<Inbox />} />
      </Routes>
    </BrowserRouter>
  </React.StrictMode>
)
