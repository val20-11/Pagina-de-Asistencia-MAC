import { useState, useEffect } from 'react'
import '../../styles/LandingPage.css'

const LandingPage = ({ onLoginClick }) => {
    const [cursorPos, setCursorPos] = useState({ x: 0, y: 0 })

    useEffect(() => {
        const handleMouseMove = (e) => {
            setCursorPos({ x: e.clientX, y: e.clientY })
        }

        document.addEventListener('mousemove', handleMouseMove)
        return () => document.removeEventListener('mousemove', handleMouseMove)
    }, [])

    const handleLoginClick = () => {
        if (onLoginClick) {
            onLoginClick()
        }
    }

    return (
        <div className="landing-page">
            <div
                className="cursor-glow"
                style={{ left: cursorPos.x, top: cursorPos.y }}
            />

            <nav className="landing-nav">
                <div className="landing-logo">
                    <img src="/images/escudo.png" alt="UNAM" className="logo-unam" />
                    <div className="logo-text">
                        <span className="logo-line1">Matemáticas Aplicadas</span>
                        <span className="logo-line2">y Computación</span>
                    </div>
                </div>
                <div className="landing-nav-right">
                    <div className="landing-logo-right">
                        <img src="/images/logo.png" alt="FES Acatlán" className="logo-fes" />
                    </div>
                    <button
                        className="landing-login-btn"
                        onClick={handleLoginClick}
                    >
                        Iniciar Sesión
                    </button>
                </div>
            </nav>

            <section className="landing-hero">
                <div className="floating-shapes">
                    <div className="shape shape-1"></div>
                    <div className="shape shape-2"></div>
                    <div className="shape shape-3"></div>
                </div>
                <div className="hero-content">
                    <h1 className="hero-title">
                        Sistema de Asistencia <span className="gradient-text">MAC</span>
                    </h1>
                    <p className="hero-subtitle">Tu portal de eventos académicos</p>
                    <p className="hero-description">
                        Registra tu asistencia, consulta eventos y mantén un seguimiento completo de tu
                        participación en las actividades de la Semana Academica.
                    </p>
                </div>
            </section>

            <section className="landing-services">
                <h2 className="section-title">
                    Acceso <span className="gradient-text">rápido</span>
                </h2>
                <div className="services-grid">
                    <div className="service-card">
                        <div className="service-icon">👨‍🎓</div>
                        <h3>Estudiantes y Asistentes</h3>
                        <p>
                            Inicia sesión con tu número de cuenta para registrar tu asistencia y acceder a
                            todos los eventos académicos disponibles
                        </p>
                    </div>
                    <div className="service-card">
                        <div className="service-icon">🎫</div>
                        <h3>Visitantes</h3>
                        <p>
                            Solicita acceso para participar en nuestros eventos con un asistente y formar
                            parte de la comunidad académica
                        </p>
                    </div>
                </div>
            </section>

            <footer className="landing-footer">
                <p>&copy; Desarrollado por:</p>
                <p>Cabrera Montero Alexis</p>
                <p>Diaz Diaz Oswaldo</p>
                <p>López Martínez Valeria</p>
                <p>&copy; 2025 FES Acatlán - UNAM. Todos los derechos reservados.</p>
            </footer>
        </div>
    )
}

export default LandingPage
