import { useState, useEffect, useRef } from 'react'
import { apiRequest } from '../../services/api'

const AttendancePanel = () => {
    const [selectedEvent, setSelectedEvent] = useState('')
    const [studentAccount, setStudentAccount] = useState('')
    const [events, setEvents] = useState([])
    const [recentAttendances, setRecentAttendances] = useState([])
    const [message, setMessage] = useState('')
    const [messageType, setMessageType] = useState('')
    const [showExternalForm, setShowExternalForm] = useState(false)
    const [externalUser, setExternalUser] = useState({
        account_number: '',
        full_name: ''
    })
    const [searchQuery, setSearchQuery] = useState('')
    const [searchResults, setSearchResults] = useState([])
    const [searching, setSearching] = useState(false)
    const [isEventFixed, setIsEventFixed] = useState(false)
    const inputRef = useRef(null)
    // Estados para el escáner removidos - ahora se usa escáner USB físico

    useEffect(() => {
        fetchEvents()
        fetchRecentAttendances()

        // Actualizar lista de eventos cada minuto para mantener solo eventos activos
        const intervalId = setInterval(() => {
            fetchEvents()
        }, 60000) // 60 segundos

        return () => clearInterval(intervalId)
    }, [])

    // Auto-seleccionar el primer evento cuando la lista de eventos cambie (solo si no está fijado)
    useEffect(() => {
        if (events.length > 0 && !selectedEvent && !isEventFixed) {
            setSelectedEvent(events[0].id)
        }
    }, [events])

    // Auto-registrar cuando se complete un número de cuenta de 8 dígitos
    useEffect(() => {
        if (studentAccount.length === 8 && selectedEvent) {
            registerAttendance()
        }
    }, [studentAccount])

    // Mantener el foco en el campo de entrada para escaneo continuo
    useEffect(() => {
        if (inputRef.current) {
            inputRef.current.focus()
        }
    }, [message, recentAttendances])

    // useEffect de Quagga eliminado - ahora se usa pyzbar

    const fetchEvents = async () => {
        try {
            // Primero obtenemos la configuración del sistema
            const configResponse = await apiRequest('/auth/system-config/')
            const config = configResponse

            const response = await apiRequest('/events/')
            const allEvents = response.results || response

            console.log('📅 Todos los eventos recibidos:', allEvents)
            console.log('⚙️ Configuración del sistema:', config)

            // Obtener la hora actual del navegador
            const now = new Date()
            console.log('🕐 Hora actual (navegador):', now)

            // Usar valores por defecto si no hay configuración
            const minutesBefore = config?.minutes_before_event || 10
            const minutesAfter = config?.minutes_after_start || 25

            const activeEvents = allEvents.filter(event => {
                // Crear fecha del evento en zona horaria local
                const eventDate = new Date(event.date + 'T00:00:00')
                const startTime = new Date(event.date + 'T' + event.start_time)
                const endTime = new Date(event.date + 'T' + event.end_time)

                // Calcular ventana de registro según configuración
                const registrationStart = new Date(startTime.getTime() - (minutesBefore * 60 * 1000))
                const registrationEnd = new Date(startTime.getTime() + (minutesAfter * 60 * 1000))

                // Obtener solo la fecha sin hora para comparación
                const eventDateOnly = new Date(eventDate.getFullYear(), eventDate.getMonth(), eventDate.getDate())
                const nowDateOnly = new Date(now.getFullYear(), now.getMonth(), now.getDate())

                // Evento activo si es hoy y está en la ventana de registro
                const isToday = eventDateOnly.getTime() === nowDateOnly.getTime()
                const isInRegistrationWindow = now >= registrationStart && now <= registrationEnd

                console.log(`📌 Evento: ${event.title}`)
                console.log(`   Fecha evento: ${eventDateOnly}`)
                console.log(`   Fecha hoy: ${nowDateOnly}`)
                console.log(`   Es hoy: ${isToday}`)
                console.log(`   Inicio evento: ${startTime}`)
                console.log(`   Ventana registro: ${registrationStart} - ${registrationEnd}`)
                console.log(`   Ahora: ${now}`)
                console.log(`   En ventana de registro: ${isInRegistrationWindow}`)
                console.log(`   Activo: ${isToday && isInRegistrationWindow}`)

                return isToday && isInRegistrationWindow
            })

            console.log('✅ Eventos disponibles para registro:', activeEvents)
            setEvents(activeEvents)
        } catch (error) {
            console.error('Error fetching events:', error)
        }
    }

    const fetchRecentAttendances = async () => {
        try {
            const response = await apiRequest('/attendance/recent/')
            setRecentAttendances(response)
        } catch (error) {
            console.error('Error fetching recent attendances:', error)
        }
    }

    const registerAttendance = async () => {
        if (!selectedEvent || !studentAccount) {
            setMessage('Selecciona un evento e ingresa el número de cuenta')
            setMessageType('error')
            return
        }

        try {
            const response = await apiRequest('/attendance/', {
                method: 'POST',
                body: {
                    event_id: selectedEvent,
                    account_number: studentAccount,
                    registration_method: 'manual'
                }
            })

            setMessage(response.message)
            setMessageType('success')
            setStudentAccount('')

            fetchRecentAttendances()

        } catch (error) {
            const errorMessage = error.response?.data?.error || 'Error de conexión'
            setMessage(`Error: ${errorMessage}`)
            setMessageType('error')
        }
    }

    const createExternalUser = async (e) => {
        e.preventDefault()

        if (!externalUser.account_number || !externalUser.full_name) {
            setMessage('Número de cuenta y nombre completo son requeridos')
            setMessageType('error')
            return
        }

        if (!/^\d{8}$/.test(externalUser.account_number)) {
            setMessage('El número de cuenta debe tener exactamente 8 dígitos')
            setMessageType('error')
            return
        }

        try {
            const response = await apiRequest('/events/external/register/', {
                method: 'POST',
                body: externalUser
            })

            setMessage(`Usuario externo creado: ${response.full_name} - Cuenta: ${response.account_number}`)
            setMessageType('success')
            setExternalUser({ account_number: '', full_name: '' })
            setShowExternalForm(false)

        } catch (error) {
            const errorMessage = error.response?.data?.error || 'Error al crear usuario externo'
            setMessage(`Error: ${errorMessage}`)
            setMessageType('error')
        }
    }

    const searchExternalUsers = async () => {
        if (!searchQuery.trim()) {
            setSearchResults([])
            return
        }

        setSearching(true)
        try {
            const response = await apiRequest(`/events/external/search/?q=${encodeURIComponent(searchQuery)}`)
            setSearchResults(response.results || [])
            if (response.count === 0) {
                setMessage('No se encontraron usuarios externos')
                setMessageType('error')
            }
        } catch (error) {
            const errorMessage = error.response?.data?.error || 'Error al buscar usuarios externos'
            setMessage(`Error: ${errorMessage}`)
            setMessageType('error')
            setSearchResults([])
        } finally {
            setSearching(false)
        }
    }

    const handleSearchKeyPress = (e) => {
        if (e.key === 'Enter') {
            searchExternalUsers()
        }
    }

    // Funciones de escáner eliminadas - El escáner USB funciona automáticamente como teclado

    return (
        <div>
            <h2 style={{ fontSize: '1.5rem', fontWeight: '600', marginBottom: '1rem', color: '#1e3a8a' }}>
                Registro de Asistencia
            </h2>

            {message && (
                <div style={{
                    padding: '1rem',
                    marginBottom: '1rem',
                    borderRadius: '0.5rem',
                    backgroundColor: messageType === 'success' ? '#dcfdf7' : '#fef2f2',
                    color: messageType === 'success' ? '#065f46' : '#991b1b',
                    border: `1px solid ${messageType === 'success' ? '#10b981' : '#ef4444'}`,
                    position: 'relative'
                }}>
                    {message}
                    <button
                        onClick={() => setMessage('')}
                        style={{
                            position: 'absolute',
                            right: '10px',
                            top: '10px',
                            background: 'none',
                            border: 'none',
                            cursor: 'pointer',
                            fontSize: '18px',
                            fontWeight: 'bold'
                        }}
                    >
                        ×
                    </button>
                </div>
            )}

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem', marginBottom: '2rem' }}>
                <div style={{ backgroundColor: 'white', padding: '1.5rem', borderRadius: '0.5rem', boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)' }}>
                    <h3 style={{ marginBottom: '1rem', color: '#374151' }}>Escaneo Rápido de Asistencia</h3>

                    {/* Selector de eventos */}
                    <div style={{ marginBottom: '1.5rem' }}>
                        <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600', color: '#1e3a8a' }}>
                            Seleccionar Evento
                        </label>
                        <select
                            value={selectedEvent}
                            onChange={(e) => setSelectedEvent(e.target.value)}
                            style={{
                                width: '100%',
                                padding: '0.75rem',
                                border: '1px solid #d1d5db',
                                borderRadius: '0.375rem',
                                backgroundColor: 'white',
                                cursor: 'pointer',
                                color: '#1e3a8a'
                            }}
                        >
                            <option value="">
                                {events.length === 0 ? 'No hay eventos activos' : 'Selecciona un evento...'}
                            </option>
                            {events.map((event) => (
                                <option key={event.id} value={event.id}>
                                    {event.title} - {event.start_time} a {event.end_time}
                                </option>
                            ))}
                        </select>
                        {events.length === 0 && (
                            <p style={{ marginTop: '0.5rem', fontSize: '0.875rem', color: '#6b7280', fontStyle: 'italic' }}>
                            Los eventos activos aparecerán automáticamente cuando comiencen
                            </p>
                        )}
                    </div>

                    <div style={{ marginBottom: '1rem' }}>
                        <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600', color: '#1e3a8a', fontSize: '1.125rem' }}>
                            Número de Cuenta (8 dígitos)
                        </label>
                        <input
                            ref={inputRef}
                            type="text"
                            value={studentAccount}
                            onChange={(e) => {
                                const value = e.target.value.replace(/\D/g, '').slice(0, 8)
                                setStudentAccount(value)
                            }}
                            placeholder="Escanea o escribe..."
                            maxLength="8"
                            autoFocus
                            style={{
                                width: '100%',
                                padding: '1rem',
                                border: '2px solid #2563eb',
                                borderRadius: '0.5rem',
                                fontSize: '1.5rem',
                                textAlign: 'center',
                                fontWeight: '600',
                                color: '#1e3a8a'
                            }}
                        />
                        <p style={{ fontSize: '0.875rem', color: '#059669', marginTop: '0.75rem', fontWeight: '500', textAlign: 'center' }}>
                            ✓ El registro es automático al completar 8 dígitos
                        </p>
                        <p style={{ fontSize: '0.75rem', color: '#6b7280', marginTop: '0.5rem', textAlign: 'center' }}>
                            Usa el escáner USB o escribe manualmente
                        </p>
                    </div>

                    {/* Botón de registro manual */}
                    <button
                        onClick={registerAttendance}
                        disabled={!selectedEvent || !studentAccount}
                        style={{
                            width: '100%',
                            backgroundColor: '#2563eb',
                            color: 'white',
                            padding: '0.75rem',
                            borderRadius: '0.375rem',
                            border: 'none',
                            fontWeight: '600',
                            cursor: (!selectedEvent || !studentAccount) ? 'not-allowed' : 'pointer',
                            opacity: (!selectedEvent || !studentAccount) ? 0.5 : 1,
                            marginTop: '0.5rem'
                        }}
                    >
                        Registrar Manualmente
                    </button>
                    <p style={{ fontSize: '0.75rem', color: '#6b7280', marginTop: '0.5rem', textAlign: 'center', fontStyle: 'italic' }}>
                        (Usar solo si el escáner no funciona)
                    </p>
                </div>

                <div style={{ backgroundColor: 'white', padding: '1.5rem', borderRadius: '0.5rem', boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)' }}>
                    <h3 style={{ marginBottom: '1rem', color: '#374151' }}>Asistencias Recientes</h3>
                    <div style={{ maxHeight: '300px', overflowY: 'auto' }}>
                        {recentAttendances.length > 0 ? (
                            recentAttendances.map((attendance, index) => (
                                <div key={index} style={{ padding: '0.5rem', borderBottom: '1px solid #535252ff', fontSize: '0.875rem', color: '#1e3a8a' }}>
                                    {attendance.attendee_name} - {attendance.event_title}
                                </div>
                            ))
                        ) : (
                            <p style={{ color: '#6b7280', fontStyle: 'italic' }}>No hay registros recientes</p>
                        )}
                    </div>
                </div>
            </div>

            {/* Sección de Buscar Usuarios Externos */}
            <div style={{ backgroundColor: 'white', padding: '1.5rem', borderRadius: '0.5rem', boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)', marginBottom: '2rem' }}>
                <h3 style={{ color: '#374151', marginBottom: '1rem' }}>Buscar Usuarios Externos</h3>
                <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem' }}>
                    <input
                        type="text"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        onKeyPress={handleSearchKeyPress}
                        placeholder="Buscar por nombre o número de cuenta..."
                        style={{
                            flex: 1,
                            padding: '0.75rem',
                            border: '1px solid #d1d5db',
                            borderRadius: '0.375rem',
                            fontSize: '0.875rem'
                        }}
                    />
                    <button
                        onClick={searchExternalUsers}
                        disabled={searching}
                        style={{
                            backgroundColor: '#2563eb',
                            color: 'white',
                            padding: '0.75rem 1.5rem',
                            borderRadius: '0.375rem',
                            border: 'none',
                            cursor: searching ? 'not-allowed' : 'pointer',
                            fontWeight: '500',
                            opacity: searching ? 0.5 : 1
                        }}
                    >
                        {searching ? 'Buscando...' : 'Buscar'}
                    </button>
                </div>

                {searchResults.length > 0 && (
                    <div style={{ marginTop: '1rem', border: '1px solid #e5e7eb', borderRadius: '0.375rem', overflow: 'hidden' }}>
                        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                            <thead style={{ backgroundColor: '#f9fafb' }}>
                                <tr>
                                    <th style={{ padding: '0.75rem', textAlign: 'left', fontSize: '0.75rem', fontWeight: '600', color: '#6b7280', textTransform: 'uppercase' }}>
                                        Número de Cuenta
                                    </th>
                                    <th style={{ padding: '0.75rem', textAlign: 'left', fontSize: '0.75rem', fontWeight: '600', color: '#6b7280', textTransform: 'uppercase' }}>
                                        Nombre Completo
                                    </th>
                                    <th style={{ padding: '0.75rem', textAlign: 'left', fontSize: '0.75rem', fontWeight: '600', color: '#6b7280', textTransform: 'uppercase' }}>
                                        Fecha Creación
                                    </th>
                                </tr>
                            </thead>
                            <tbody>
                                {searchResults.map((user) => (
                                    <tr key={user.id} style={{ borderTop: '1px solid #e5e7eb' }}>
                                        <td style={{ padding: '0.75rem', fontSize: '0.875rem', fontWeight: '600', color: '#1e3a8a' }}>
                                            {user.account_number}
                                        </td>
                                        <td style={{ padding: '0.75rem', fontSize: '0.875rem', color: '#374151' }}>
                                            {user.full_name}
                                        </td>
                                        <td style={{ padding: '0.75rem', fontSize: '0.875rem', color: '#6b7280' }}>
                                            {user.created_at}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>

            {/* Sección de Crear Usuario Externo */}
            <div style={{ backgroundColor: 'white', padding: '1.5rem', borderRadius: '0.5rem', boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                    <h3 style={{ color: '#374151', margin: 0 }}>Crear Usuario Externo</h3>
                    <button
                        onClick={() => setShowExternalForm(!showExternalForm)}
                        style={{
                            backgroundColor: '#2563eb',
                            color: 'white',
                            padding: '0.5rem 1rem',
                            borderRadius: '0.375rem',
                            border: 'none',
                            cursor: 'pointer',
                            fontWeight: '500'
                        }}
                    >
                        {showExternalForm ? 'Cancelar' : '+ Nuevo Usuario Externo'}
                    </button>
                </div>

                {showExternalForm && (
                    <form onSubmit={createExternalUser} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginTop: '1rem' }}>
                        <div>
                            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500', color: '#1e3a8a', fontSize: '0.875rem' }}>
                                Número de Cuenta (8 dígitos) *
                            </label>
                            <input
                                type="text"
                                value={externalUser.account_number}
                                onChange={(e) => {
                                    const value = e.target.value.replace(/\D/g, '').slice(0, 8)
                                    setExternalUser({ ...externalUser, account_number: value })
                                }}
                                placeholder="12345678"
                                maxLength="8"
                                required
                                style={{ width: '100%', padding: '0.5rem', border: '1px solid #d1d5db', borderRadius: '0.375rem' }}
                            />
                        </div>
                        <div>
                            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500', color: '#1e3a8a', fontSize: '0.875rem' }}>
                                Nombre Completo *
                            </label>
                            <input
                                type="text"
                                value={externalUser.full_name}
                                onChange={(e) => setExternalUser({ ...externalUser, full_name: e.target.value })}
                                placeholder="Juan Pérez López"
                                required
                                style={{ width: '100%', padding: '0.5rem', border: '1px solid #d1d5db', borderRadius: '0.375rem' }}
                            />
                        </div>
                        <div style={{ gridColumn: '1 / -1' }}>
                            <button
                                type="submit"
                                style={{
                                    backgroundColor: '#059669',
                                    color: 'white',
                                    padding: '0.75rem 1.5rem',
                                    borderRadius: '0.375rem',
                                    border: 'none',
                                    cursor: 'pointer',
                                    fontWeight: '600',
                                    width: '100%'
                                }}
                            >
                                Crear Usuario Externo
                            </button>
                        </div>
                    </form>
                )}

                <p style={{ fontSize: '0.875rem', color: '#6b7280', marginTop: '1rem', fontStyle: 'italic' }}>
                    Los usuarios externos son aprobados automáticamente y pueden acceder con su número de cuenta.
                </p>
            </div>

            {/* Modal del escáner eliminado - Ahora se usa escáner USB físico */}
        </div>
    )
}

export default AttendancePanel