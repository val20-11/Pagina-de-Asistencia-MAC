import { useState, useEffect } from 'react'
import { useAuth } from '../../contexts/AuthContext'
import { apiRequest } from '../../services/api'
import '../../styles/Login.css'

const Login = () => {
    const [accountNumber, setAccountNumber] = useState('')
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')
    const [cursorPos, setCursorPos] = useState({ x: 0, y: 0 })

    const { login } = useAuth()

    useEffect(() => {
        const handleMouseMove = (e) => {
            setCursorPos({ x: e.clientX, y: e.clientY })
        }

        document.addEventListener('mousemove', handleMouseMove)
        return () => document.removeEventListener('mousemove', handleMouseMove)
    }, [])

    const handleSubmit = async (e) => {
        e.preventDefault()
        setLoading(true)
        setError('')

        // Validar formato: 7 dígitos
        if (!/^\d{7}$/.test(accountNumber)) {
            setError('El número de cuenta debe tener exactamente 7 dígitos')
            setLoading(false)
            return
        }

        try {
            const response = await apiRequest('/auth/login/', {
                method: 'POST',
                body: { account_number: accountNumber }
            })
            login(response.user, response.tokens)
        } catch (err) {
            setError('Número de cuenta no encontrado o no autorizado.')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="login-container">
            {/* Cursor Glow Effect */}
            <div
                className="login-cursor-glow"
                style={{ left: cursorPos.x, top: cursorPos.y }}
            />

            {/* Floating Shapes Background */}
            <div className="login-floating-shapes">
                <div className="login-shape login-shape-1"></div>
                <div className="login-shape login-shape-2"></div>
                <div className="login-shape login-shape-3"></div>
            </div>

            <div className="login-card">
                <div className="login-header">
                    <div className="login-logo">
                        <img src="/images/logo.png" alt="FES Acatlán - UNAM" className="login-logo-img" />
                    </div>
                    <h1 className="login-title">
                        Sistema de Asistencia MAC
                    </h1>
                </div>

                <form onSubmit={handleSubmit} className="login-form">
                    <div className="login-input-group">
                        <label className="login-label">
                            Número de Cuenta
                        </label>
                        <input
                            type="text"
                            value={accountNumber}
                            onChange={(e) => {
                                const value = e.target.value.replace(/\D/g, '').slice(0, 7)
                                setAccountNumber(value)
                            }}
                            className="login-input"
                            placeholder="1234567"
                            required
                            disabled={loading}
                            maxLength="7"
                        />
                        <small className="login-input-hint">
                            Ingresa tu número de cuenta de 7 dígitos
                        </small>
                    </div>

                    {error && (
                        <div className="login-error">
                            {error}
                        </div>
                    )}

                    {/* Botón Iniciar Sesión */}
                    <button
                        type="submit"
                        className="login-btn"
                        disabled={loading}
                    >
                        {loading ? 'Ingresando...' : 'Ingresar'}
                    </button>
                </form>

                <div className="login-footer">
                    <p className="login-footer-text">
                        Estudiantes: Consulta tus asistencias<br />
                        Asistentes: Registra asistencias<br />
                        <span style={{ fontSize: '0.8rem' }}>Los usuarios externos deben solicitar su cuenta al asistente</span>
                    </p>
                </div>
            </div>
        </div>
    )
}

export default Login
