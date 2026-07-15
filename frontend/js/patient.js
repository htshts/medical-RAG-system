/**
 * Medical RAG System - Patient Detail Page Logic
 */

document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const loadingEl = document.getElementById('loading');
    const errorAlert = document.getElementById('errorAlert');
    const patientContent = document.getElementById('patientContent');
    const patientName = document.getElementById('patientName');
    const patientMeta = document.getElementById('patientMeta');
    const timelineContent = document.getElementById('timelineContent');
    const recordsContent = document.getElementById('recordsContent');
    const entitiesContent = document.getElementById('entitiesContent');
    const summaryContent = document.getElementById('summaryContent');
    const searchInput = document.getElementById('searchInput');
    const searchBtn = document.getElementById('searchBtn');
    const generateSummaryBtn = document.getElementById('generateSummaryBtn');

    // State
    let currentPatientId = null;

    // Initialize
    init();

    function init() {
        // Get patient ID from URL
        const urlParams = new URLSearchParams(window.location.search);
        currentPatientId = urlParams.get('id');

        if (!currentPatientId) {
            showError('未提供患者ID');
            loadingEl.classList.remove('active');
            return;
        }

        // Load patient data
        loadPatientData(currentPatientId);

        // Tab handlers
        document.querySelectorAll('.tab').forEach(tab => {
            tab.addEventListener('click', () => {
                document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
                document.querySelectorAll('.tab-content').forEach(tc => tc.classList.remove('active'));
                
                tab.classList.add('active');
                document.getElementById(`tab-${tab.dataset.tab}`).classList.add('active');
            });
        });

        // Search handler
        searchBtn.addEventListener('click', () => {
            const query = searchInput.value.trim();
            if (query) {
                window.location.href = `/patient.html?id=${encodeURIComponent(query)}`;
            }
        });

        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') searchBtn.click();
        });

        // Generate summary handler
        generateSummaryBtn.addEventListener('click', () => {
            window.location.href = `/summary.html?patient_id=${currentPatientId}`;
        });
    }

    async function loadPatientData(patientId) {
        loadingEl.classList.add('active');
        patientContent.classList.add('hidden');
        hideError();

        try {
            // Load patient info and timeline in parallel
            const [patientData, timelineData] = await Promise.all([
                api.getPatient(patientId),
                api.getPatientTimeline(patientId).catch(() => null)
            ]);

            displayPatientInfo(patientData);
            
            if (timelineData) {
                displayTimeline(timelineData);
            }

            patientContent.classList.remove('hidden');
        } catch (error) {
            showError(`加载患者信息失败: ${error.message}`);
        } finally {
            loadingEl.classList.remove('active');
        }
    }

    function displayPatientInfo(data) {
        const patient = data.patient || data;

        // Name
        patientName.textContent = patient.name || patient.patient_id || '未知患者';

        // Meta info
        const metaItems = [];
        if (patient.age) metaItems.push(`🎂 ${patient.age}岁`);
        if (patient.gender) metaItems.push(`👤 ${patient.gender}`);
        if (patient.patient_id) metaItems.push(`🆔 ${patient.patient_id}`);
        if (patient.phone) metaItems.push(`📞 ${patient.phone}`);
        
        patientMeta.innerHTML = metaItems.map(item => 
            `<span class="patient-meta-item">${item}</span>`
        ).join('');

        // Records
        if (patient.records && patient.records.length > 0) {
            displayRecords(patient.records);
        }

        // Entities
        if (patient.entities) {
            displayEntities(patient.entities);
        }
    }

    function displayTimeline(data) {
        const events = data.timeline || data.events || [];
        
        if (events.length === 0) {
            timelineContent.innerHTML = '<p class="text-muted text-center">暂无时间轴数据</p>';
            return;
        }

        timelineContent.innerHTML = events.map(event => `
            <div class="timeline-item">
                <div class="timeline-date">${formatDate(event.date || event.time)}</div>
                <div class="timeline-title">${escapeHtml(event.title || event.type || '就诊事件')}</div>
                <div class="timeline-content">
                    ${event.description ? escapeHtml(event.description) : ''}
                    ${event.department ? `<div style="margin-top:0.5rem;color:var(--text-secondary);">科室: ${escapeHtml(event.department)}</div>` : ''}
                </div>
            </div>
        `).join('');
    }

    function displayRecords(records) {
        recordsContent.innerHTML = records.map(record => `
            <div class="card">
                <div class="result-header">
                    <span class="result-title">${escapeHtml(record.record_type || '就诊记录')}</span>
                    <span class="result-score">${formatDate(record.visit_time)}</span>
                </div>
                <div class="result-meta">
                    ${record.department ? `<span class="result-meta-item">🏥 ${escapeHtml(record.department)}</span>` : ''}
                    ${record.doctor ? `<span class="result-meta-item">👨‍⚕️ ${escapeHtml(record.doctor)}</span>` : ''}
                </div>
                <div class="result-content">
                    ${record.content ? escapeHtml(record.content.substring(0, 300)) + (record.content.length > 300 ? '...' : '') : '无详细内容'}
                </div>
            </div>
        `).join('');
    }

    function displayEntities(entities) {
        const categories = {
            disease: { label: '疾病诊断', items: entities.diseases || [] },
            symptom: { label: '症状', items: entities.symptoms || [] },
            medication: { label: '药物', items: entities.medications || [] },
            test: { label: '检查项目', items: entities.tests || [] },
        };

        entitiesContent.innerHTML = Object.entries(categories).map(([key, cat]) => `
            <div class="card">
                <div class="card-header">${cat.label}</div>
                <div>
                    ${cat.items.length > 0 ? 
                        cat.items.map(item => `
                            <span class="entity-tag entity-${key}">${escapeHtml(item.name || item)}</span>
                        `).join('') : 
                        '<p class="text-muted">无数据</p>'
                    }
                </div>
            </div>
        `).join('');
    }

    // Utility functions
    function formatDate(dateStr) {
        if (!dateStr) return '';
        const date = new Date(dateStr);
        return date.toLocaleDateString('zh-CN', { 
            year: 'numeric', 
            month: '2-digit', 
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    function showError(message) {
        errorAlert.textContent = message;
        errorAlert.classList.remove('hidden');
    }

    function hideError() {
        errorAlert.classList.add('hidden');
    }
});
