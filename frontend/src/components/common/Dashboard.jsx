import { useState, useEffect } from 'react'
import { useAuth } from '../../contexts/AuthContext'
import AdminPanel from '../admin/AdminPanel'
import AttendancePanel from '../attendance/AttendancePanel'
import StudentPanel from '../student/StudentPanel'
import '../../styles/Dashboard.css'

const Dashboard = () => {
    const { user, logout } = useAuth()
    const [isDarkMode, setIsDarkMode] = useState(() => {
        // Recuperar preferencia guardada o usar false por defecto
        const saved = localStorage.getItem('theme')
        return saved === 'dark'
    })

    const isAssistant = user.profile?.user_type === 'assistant'
    const isAdmin = user.is_staff || user.is_superuser

    useEffect(() => {
        // Guardar preferencia
        localStorage.setItem('theme', isDarkMode ? 'dark' : 'light')

        // Aplicar clase al body cuando el componente esté montado
        if (isDarkMode) {
            document.body.classList.add('dark-theme')
        } else {
            document.body.classList.remove('dark-theme')
        }

        // Limpiar la clase cuando el componente se desmonte (al cerrar sesión)
        return () => {
            document.body.classList.remove('dark-theme')
        }
    }, [isDarkMode])

    const toggleTheme = () => {
        setIsDarkMode(!isDarkMode)
    }

    return (
        <div className="dashboard">
            <nav className="dashboard-nav">
                <div className="dashboard-nav-container">
                    <h1 className="dashboard-title">
                        Sistema MAC - {isAdmin ? 'Administrador' : isAssistant ? 'Asistente' : 'Estudiante'}
                    </h1>
                    <div className="dashboard-nav-actions">
                        <span className="dashboard-user-name">
                            Hola, {user.profile?.full_name || user.first_name}
                        </span>
                        <button
                            onClick={toggleTheme}
                            className="dashboard-theme-btn"
                            title={isDarkMode ? 'Cambiar a tema claro' : 'Cambiar a tema oscuro'}
                        >
                            {isDarkMode ? '☀️' : '🌙'}
                        </button>
                        <button
                            onClick={logout}
                            className="dashboard-logout-btn"
                        >
                            Cerrar Sesión
                        </button>
                    </div>
                </div>
            </nav>

            <div className="dashboard-content">
                {isAdmin ? (
                    <AdminPanel />
                ) : isAssistant ? (
                    <AttendancePanel />
                ) : (
                    <StudentPanel />
                )}
            </div>
        </div>
    )
}

export default Dashboard