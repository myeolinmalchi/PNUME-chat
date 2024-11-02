import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import './reset.css'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import Layout from 'components/layouts'

const router = createBrowserRouter([
  {
    element: <Layout/>, 
    children: [
      {
        path: '/', 
        element: <></>
      }
    ]
  }
])

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <RouterProvider router={router}/>
  </StrictMode>,
)
