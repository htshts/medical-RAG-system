/**
 * Medical RAG System - API Communication Layer
 * Handles all communication with the backend server
 */

const API_BASE = '/api/v1';

class ApiClient {
    constructor() {
        this.baseUrl = API_BASE;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
        };

        const config = { ...defaultOptions, ...options };

        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `HTTP ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API Request failed:', error);
            throw error;
        }
    }

    // Query endpoints
    async search(query, options = {}) {
        return this.request('/query/search', {
            method: 'POST',
            body: JSON.stringify({
                query,
                patient_id: options.patientId || null,
                top_k: options.topK || 10,
                enable_time_align: options.enableTimeAlign !== false,
            }),
        });
    }

    async getSuggestions(query) {
        return this.request('/query/suggest', {
            method: 'POST',
            body: JSON.stringify({ query, limit: 5 }),
        });
    }

    // Patient endpoints
    async getPatient(patientId) {
        return this.request(`/patient/${patientId}`);
    }

    async getPatientTimeline(patientId) {
        return this.request(`/patient/${patientId}/timeline`);
    }

    async searchPatients(query) {
        return this.request('/patient/search', {
            method: 'POST',
            body: JSON.stringify({ query, limit: 20 }),
        });
    }

    // Summary endpoints
    async generateSummary(patientId, options = {}) {
        return this.request('/summary/generate', {
            method: 'POST',
            body: JSON.stringify({
                patient_id: patientId,
                summary_type: options.type || 'transfer',
                include_sections: options.sections || ['chief_complaint', 'history', 'examination', 'diagnosis', 'treatment'],
                time_window_days: options.timeWindow || 30,
            }),
        });
    }

    async getSummary(patientId, summaryId) {
        return this.request(`/summary/${patientId}/${summaryId}`);
    }

    async getSummaryTemplates() {
        return this.request('/summary/templates');
    }

    // Health check
    async healthCheck() {
        return this.request('/health');
    }
}

// Create global API instance
window.api = new ApiClient();
