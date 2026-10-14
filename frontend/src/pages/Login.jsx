import { useState } from "react"
import { Link, useLocation, useNavigate } from "react-router-dom"
import api from "../api"

function getErrorMessage(error) {
  const detail = error.response?.data?.detail

  // Our own messages, like "Invalid email or password"
  if (typeof detail === "string") return detail

  // Validation messages
  if (Array.isArray(detail) && detail.length > 0) {
    return detail[0].msg.replace("Value error, ", "")
  }

  return "Something went wrong. Please try again."
}

export default function Login() {
  const navigate = useNavigate()
  const location = useLocation()

  // True when we arrive here right after registering
  const justRegistered = location.state?.registered

  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    setError("")
    setLoading(true)

    try {
      await api.post("/auth/login", { email, password })
      navigate("/dashboard")
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-900 p-4">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-md rounded-2xl bg-white p-8 shadow-lg"
      >
        <h1 className="mb-1 text-2xl font-bold">Welcome back</h1>
        <p className="mb-6 text-sm text-slate-500">
          Log in to analyze your resume.
        </p>

        {justRegistered && !error && (
          <p className="mb-4 rounded bg-green-100 p-3 text-sm text-green-700">
            Account created. Please log in.
          </p>
        )}

        {error && (
          <p className="mb-4 rounded bg-red-100 p-3 text-sm text-red-700">
            {error}
          </p>
        )}

        <label className="mb-1 block text-sm font-medium">Email</label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          className="mb-4 w-full rounded border border-slate-300 p-2"
        />

        <label className="mb-1 block text-sm font-medium">Password</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          className="mb-6 w-full rounded border border-slate-300 p-2"
        />

        <button
          type="submit"
          disabled={loading}
          className="w-full rounded bg-blue-600 py-2 font-semibold text-white disabled:opacity-50"
        >
          {loading ? "Logging in..." : "Log in"}
        </button>

        <p className="mt-4 text-center text-sm text-slate-600">
          New here?{" "}
          <Link to="/register" className="text-blue-600 underline">
            Create an account
          </Link>
        </p>
      </form>
    </div>
  )
}
