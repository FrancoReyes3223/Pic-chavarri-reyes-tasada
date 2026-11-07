import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import '@fontsource-variable/archivo/wdth.css'
import './index.css'
import App from './App.tsx'

// BrowserRouter lee la dirección del navegador (/grafo, /cronograma, ...)
// para que App muestre la página que corresponde.
createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </StrictMode>,
)
