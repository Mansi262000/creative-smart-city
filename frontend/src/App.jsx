import React, { useState } from 'react'
import Dashboard from './components/Dashboard.jsx'
import Login from './components/Login.jsx'

export default function App() {
  const [token, setToken] = useState(null)
  return token ? <Dashboard token={token} onLogout={()=>setToken(null)} /> : <Login onLogin={setToken} />
}
