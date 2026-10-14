import { useEffect, useState } from "react"
import {
  BrowserRouter,
  Routes,
  Route,
  Link,
  useNavigate,
} from "react-router-dom"
import api from "./api"
import Register from "./pages/Register"
import Login from "./pages/Login"

function Home() {
  return (
    <div className="p-6">
      <h1 className="mb-4 text-3xl font-bold">ResuMetrX</h1>
      <Link to="/login" className="mr-4 text-blue-600 underline">
        Log in
      </Link>
      <Link to="/register" className="text-blue-600 underline">
        Register
      </Link>
    </div>
  )
}

function Dashboard() {
  const navigate = useNavigate()
  const [user, setUser] = useState(null)

  useEffect(() => {
    api
      .get("/auth/me")
      .then((response) => setUser(response.data))
      .catch(() => navigate("/login"))
  }, [navigate])

  async function handleLogout() {
    try {
      await api.post("/auth/logout")
    } finally {
      navigate("/login")
    }
  }

  if (!user) return <p className="p-6">Loading...</p>

  return (
    <div className="p-6">
      <h1 className="mb-2 text-2xl font-bold">Hello, {user.name}!</h1>
      <p className="mb-4 text-slate-600">{user.email}</p>
      <button
        onClick={handleLogout}
        className="rounded bg-slate-800 px-4 py-2 text-white"
      >
        Log out
      </button>
    </div>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/register" element={<Register />} />
        <Route path="/login" element={<Login />} />
        <Route path="/dashboard" element={<Dashboard />} />
      </Routes>
    </BrowserRouter>
  )
}