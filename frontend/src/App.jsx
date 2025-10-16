import { useState, useEffect } from 'react'
import './App.css'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import LandingPage from './components/auth/LandingPage'
import Login from './components/auth/Login'
import Dashboard from './components/common/Dashboard'

const MacAttendanceApp = () => {
    const { user, loading } = useAuth()
    const [showLogin, setShowLogin] = useState(false)

    // Resetear showLogin cuando el usuario cierra sesión
    useEffect(() => {
        if (!user) {
            setShowLogin(false)
        }
    }, [user])

    if (loading) {
        return (
            <div className="app-loading">
                <div className="app-loading-content">
                    <div className="app-loading-spinner"></div>
                    <p className="app-loading-text">Cargando sistema...</p>
                </div>
            </div>
        )
    }

    if (!user) {
        return showLogin ? <Login /> : <LandingPage onLoginClick={() => setShowLogin(true)} />
    }

    return <Dashboard />
}

function App() {
    return (
        <AuthProvider>
            <MacAttendanceApp />
        </AuthProvider>
    )
}

export default App