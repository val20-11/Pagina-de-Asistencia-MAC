import { useState, useEffect } from 'react'
import { useAuth } from '../../contexts/AuthContext'
import { apiRequest } from '../../services/api'

const StudentPanel = () => {
    const { user } = useAuth()
    const [attendanceStats, setAttendanceStats] = useState(null)
    const [allEvents, setAllEvents] = useState([])
    const [myAttendances, setMyAttendances] = useState([])
    const [loading, setLoading] = useState(true)
    const [filterMode, setFilterMode] = useState('future') // 'future' o 'attended'

    // Detectar si es usuario externo y extraer el número de cuenta
    const isExternalUser = user.username?.startsWith('ext_')
    const accountNumber = isExternalUser
        ? user.username.substring(4)  // Remover prefijo "ext_"
        : user.profile?.account_number

    useEffect(() => {
        fetchStudentData()
    }, [])

    const fetchStudentData = async () => {
        try {
            // Usar endpoints diferentes según el tipo de usuario
            const statsEndpoint = isExternalUser
                ? `/attendance/external/stats/?account_number=${accountNumber}`
                : `/attendance/stats/?account_number=${accountNumber}`

            const attendancesEndpoint = isExternalUser
                ? `/attendance/external/my/?account_number=${accountNumber}`
                : `/attendance/my/?account_number=${accountNumber}`

            const [eventsRes, statsRes, attendancesRes] = await Promise.all([
                apiRequest('/events/'),
                apiRequest(statsEndpoint),
                apiRequest(attendancesEndpoint)
            ])

            const allEventsData = eventsRes.results || eventsRes
            setAllEvents(allEventsData)
            setAttendanceStats(statsRes)
            setMyAttendances(attendancesRes)

            console.log('Eventos cargados:', allEventsData)
            console.log('Estadísticas:', statsRes)
            console.log('Mis asistencias:', attendancesRes)
        } catch (error) {
            console.error('Error fetching student data:', error)
        } finally {
            setLoading(false)
        }
    }

    const getFilteredEvents = () => {
        if (filterMode === 'attended') {
            // Obtener IDs de eventos a los que asistí
            const attendedEventIds = myAttendances.map(att => att.event)
            // Filtrar eventos por esos IDs
            return allEvents.filter(event => attendedEventIds.includes(event.id))
        } else {
            // Eventos futuros
            const now = new Date()
            return allEvents.filter(event => {
                const eventDateTime = new Date(event.date + 'T' + event.end_time)
                return eventDateTime > now
            })
        }
    }

    const events = getFilteredEvents()

    if (loading) {
        return <div style={{ textAlign: 'center', padding: '2rem' }}>Cargando información...</div>
    }

    return (
        <div>
            <h2 style={{ fontSize: '1.5rem', fontWeight: '600', marginBottom: '1rem', color: '#1e3a8a' }}>
                Asistencia
            </h2>

            <div style={{ backgroundColor: 'white', padding: '1.5rem', borderRadius: '0.5rem', boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)', marginBottom: '1.5rem' }}>
                <h3 style={{ marginBottom: '1rem', color: '#374151' }}>Estadísticas de Asistencia</h3>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem' }}>
                    <div style={{ backgroundColor: '#dbeafe', padding: '1rem', borderRadius: '0.5rem', textAlign: 'center' }}>
                        <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#1e40af' }}>
                            {attendanceStats?.attended_events || 0}
                        </div>
                        <div style={{ color: '#1e40af', fontSize: '0.875rem' }}>Eventos Asistidos</div>
                    </div>
                    <div style={{ backgroundColor: '#dcfdf7', padding: '1rem', borderRadius: '0.5rem', textAlign: 'center' }}>
                        <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#065f46' }}>
                            {attendanceStats?.total_events || 0}
                        </div>
                        <div style={{ color: '#065f46', fontSize: '0.875rem' }}>Total de Eventos</div>
                    </div>
                    <div style={{ backgroundColor: '#fef3c7', padding: '1rem', borderRadius: '0.5rem', textAlign: 'center' }}>
                        <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#92400e' }}>
                            {attendanceStats?.attendance_percentage?.toFixed(1) || 0}%
                        </div>
                        <div style={{ color: '#92400e', fontSize: '0.875rem' }}>Porcentaje</div>
                    </div>
                </div>
            </div>

            <div style={{ backgroundColor: 'white', padding: '1.5rem', borderRadius: '0.5rem', boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                    <h3 style={{ color: '#374151', margin: 0 }}>Eventos</h3>
                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                        <button
                            onClick={() => setFilterMode('future')}
                            style={{
                                padding: '0.5rem 1rem',
                                borderRadius: '0.375rem',
                                border: '1px solid',
                                borderColor: filterMode === 'future' ? '#2563eb' : '#d1d5db',
                                backgroundColor: filterMode === 'future' ? '#2563eb' : 'white',
                                color: filterMode === 'future' ? 'white' : '#374151',
                                fontWeight: filterMode === 'future' ? '600' : '400',
                                cursor: 'pointer',
                                fontSize: '0.875rem',
                                transition: 'all 0.2s',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '0.5rem'
                            }}
                        >
                            Eventos Futuros
                            <span style={{
                                backgroundColor: filterMode === 'future' ? 'rgba(255, 255, 255, 0.2)' : '#e5e7eb',
                                padding: '0.125rem 0.5rem',
                                borderRadius: '9999px',
                                fontSize: '0.75rem',
                                fontWeight: '600'
                            }}>
                                {filterMode === 'future' ? events.length : allEvents.filter(e => new Date(e.date + 'T' + e.end_time) > new Date()).length}
                            </span>
                        </button>
                        <button
                            onClick={() => setFilterMode('attended')}
                            style={{
                                padding: '0.5rem 1rem',
                                borderRadius: '0.375rem',
                                border: '1px solid',
                                borderColor: filterMode === 'attended' ? '#059669' : '#d1d5db',
                                backgroundColor: filterMode === 'attended' ? '#059669' : 'white',
                                color: filterMode === 'attended' ? 'white' : '#374151',
                                fontWeight: filterMode === 'attended' ? '600' : '400',
                                cursor: 'pointer',
                                fontSize: '0.875rem',
                                transition: 'all 0.2s',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '0.5rem'
                            }}
                        >
                            Mis Asistencias
                            <span style={{
                                backgroundColor: filterMode === 'attended' ? 'rgba(255, 255, 255, 0.2)' : '#e5e7eb',
                                padding: '0.125rem 0.5rem',
                                borderRadius: '9999px',
                                fontSize: '0.75rem',
                                fontWeight: '600'
                            }}>
                                {filterMode === 'attended' ? events.length : myAttendances.length}
                            </span>
                        </button>
                    </div>
                </div>

                {events.length > 0 ? (
                    <div>
                        {events.map((event) => (
                            <div key={event.id} style={{ padding: '1rem', borderBottom: '1px solid #e5e7eb' }}>
                                <div style={{ display: 'flex', justifyContent: 'between', alignItems: 'start' }}>
                                    <div style={{ flex: 1 }}>
                                        <h4 style={{ fontSize: '1.1rem', fontWeight: '600', marginBottom: '0.5rem', color: '#1e3a8a' }}>
                                            {event.title}
                                        </h4>
                                        <p style={{ color: '#6b7280', marginBottom: '0.5rem' }}>{event.description}</p>
                                        <div style={{ display: 'flex', gap: '1rem', fontSize: '0.875rem', color: '#6b7280' }}>
                                            <span>📅 {event.date}</span>
                                            <span>🕒 {event.start_time} - {event.end_time}</span>
                                            <span>📍 {event.location}</span>
                                            <span>👨‍🏫 {event.speaker}</span>
                                        </div>
                                    </div>
                                    <span style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem', fontWeight: '600', borderRadius: '9999px', backgroundColor: event.modality === 'presencial' ? '#dcfdf7' : '#dbeafe', color: event.modality === 'presencial' ? '#065f46' : '#1e40af' }}>
                                        {event.modality}
                                    </span>
                                </div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div style={{ padding: '2rem', textAlign: 'center' }}>
                        <p style={{ color: '#6b7280', marginBottom: '0.5rem' }}>
                            {filterMode === 'attended'
                                ? 'No tienes asistencias registradas aún'
                                : 'No hay eventos futuros programados'}
                        </p>
                        <p style={{ color: '#9ca3af', fontSize: '0.875rem' }}>
                            {filterMode === 'attended'
                                ? 'Los eventos a los que asistas aparecerán aquí'
                                : 'Los próximos eventos aparecerán cuando sean programados'}
                        </p>
                    </div>
                )}
            </div>
        </div>
    )
}

export default StudentPanel