import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'

import { routes } from "./routes";

const rootElement = document.getElementById('root')

if (rootElement) {
  ReactDOM.createRoot(rootElement).render(
    <React.StrictMode>
      <BrowserRouter basename={import.meta.env.BASE_URL}>
        <React.Suspense fallback={<div>Loading...</div>}>
          <Routes>
            {routes.map(({ path, element }) => (
              <Route key={path} path={path} element={element} />
            ))}
          </Routes>
        </React.Suspense>
      </BrowserRouter>
    </React.StrictMode>
  );
} else {
  console.error(
    "Root element not found. Make sure index.html contains <div id='root'></div>"
  );
}


