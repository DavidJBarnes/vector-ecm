import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import DocumentsPage from './routes/Documents'
import SearchPage from './routes/Search'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/documents" element={<DocumentsPage />} />
          <Route path="/search" element={<SearchPage />} />
          <Route path="*" element={<Navigate to="/documents" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
