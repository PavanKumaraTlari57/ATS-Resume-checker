import { useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import api from "../api"

function getErrorMessage(error) {
  const detail = error.response?.data?.detail

  // Our own messages, like "Email is already registered"
  if (typeof detail === "string") return detail

  // Validation messages, like the password rules
  if (Array.isArray(detail) && detail.length > 0) {
    return detail[0].msg.replace("Value error, ", "")
  }

  return "Something went wrong. Please try again."
}

export default function Register() {
  const navigate = useNavigate()

  const [name, setName] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    setError("")
    setLoading(true)

    try {
      await api.post("/auth/register", { name, email, password })
      navigate("/login", { state: { registered: true } })
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
        <h1 className="mb-1 text-2xl font-bold">Create your account</h1>
        <p className="mb-6 text-sm text-slate-500">
          Start analyzing your resume with ResuMetrX.
        </p>

        {error && (
          <p className="mb-4 rounded bg-red-100 p-3 text-sm text-red-700">
            {error}
          </p>
        )}

        <label className="mb-1 block text-sm font-medium">Name</label>
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
          maxLength={100}
          className="mb-4 w-full rounded border border-slate-300 p-2"
        />

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
          className="mb-1 w-full rounded border border-slate-300 p-2"
        />
        <p className="mb-6 text-xs text-slate-500">
          At least 12 characters, with an uppercase letter, a lowercase letter,
          a number, and a special character.
        </p>

        <button
          type="submit"
          disabled={loading}
          className="w-full rounded bg-blue-600 py-2 font-semibold text-white disabled:opacity-50"
        >
          {loading ? "Creating account..." : "Register"}
        </button>

        <p className="mt-4 text-center text-sm text-slate-600">
          Already have an account?{" "}
          <Link to="/login" className="text-blue-600 underline">
            Log in
          </Link>
        </p>
      </form>
    </div>
  )
}
