/**
 * Medical RAG System - Main Application Logic
 */

document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const searchInput = document.getElementById('searchInput');
    const searchBtn = document.getElementById('searchBtn');
    const patientIdInput = document.getElementById('patientIdInput');
    const topKInput = document.getElementById('topKInput');
    const timeAlignCheck = document.getElementById('timeAlignCheck');
    const suggestionsEl = document.getElementById('suggestions');
    const loadingEl = document.getElementById('loading');
    const resultsSection = document.getElementById('resultsSection');
    const resultsList = document.getElementById('resultsList');
    const resultCount = document.getElementById('resultCount');
    const emptyState = document.getElementById('emptyState');
    const infoAlert = document.getElementById('infoAlert');
    const errorAlert = document.getElementById('errorAlert');

    // State
    let searchTimeout = null;
    let currentQuery = '';

    // Initialize
    init();

    function init() {
        // Event listeners
        searchBtn.addEventListener('click', performSearch);
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') performSearch();
        });

        // Live suggestions
        searchInput.addEventListener('input', () => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(fetchSuggestions, 500);
        });

        // Show empty state initially
        emptyState.classList.remove('hidden');

        // Check API health
        checkHealth();
    }

    async function checkHealth() {
        try {
            await api.healthCheck();
            showInfo('系统运行正常，可以开始查询');
        } catch (error) {
            showError('无法连接到后端服务，请检查服务器是否启动');
        }
    }

    async function fetchSuggestions() {
        const query = searchInput.value.trim();
        if (query.length < 2) {
            suggestionsEl.innerHTML = '';
            return;
        }

        try {
            const data = await api.getSuggestions(query);
            if (data.suggestions && data.suggestions.length > 0) {
                suggestionsEl.innerHTML = data.suggestions.map(s => 
                    `<span class="suggestion-chip" data-query="${escapeHtml(s.text)}">${escapeHtml(s.text)}</span>`
                ).join('');

                // Add click handlers
                suggestionsEl.querySelectorAll('.suggestion-chip').forEach(chip => {
                    chip.addEventListener('click', () => {
                        searchInput.value = chip.dataset.query;
                        performSearch();
                    });
                });
            }
        } catch (error) {
            // Silently fail for suggestions
        }
    }

    async function performSearch() {
        const query = searchInput.value.trim();
        if (!query) {
            showError('请输入查询内容');
            return;
        }

        currentQuery = query;

        // Show loading
        loadingEl.classList.add('active');
        resultsSection.classList.add('hidden');
        emptyState.classList.add('hidden');
        hideAlerts();

        try {
            const results = await api.search(query, {
                patientId: patientIdInput.value.trim() || null,
                topK: parseInt(topKInput.value) || 10,
                enableTimeAlign: timeAlignCheck.checked,
            });

            displayResults(results);
        } catch (error) {
            showError(`检索失败: ${error.message}`);
            resultsSection.classList.add('hidden');
            emptyState.classList.remove('hidden');
        } finally {
            loadingEl.classList.remove('active');
        }
    }

    function displayResults(data) {
        const results = data.results || [];
        const queryInfo = data.query_info || {};

        if (results.length === 0) {
            resultsSection.classList.add('hidden');
            emptyState.classList.remove('hidden');
            emptyState.querySelector('p:nth-child(2)').textContent = '未找到相关结果';
            return;
        }

        // Update count
        resultCount.textContent = `共 ${results.length} 条结果`;
        if (queryInfo.processed_query && queryInfo.processed_query !== currentQuery) {
            resultCount.textContent += ` (原始查询: "${queryInfo.processed_query}")`;
        }

        // Render results
        resultsList.innerHTML = results.map((result, index) => {
            const score = result.score || result.relevance_score || 0;
            const doc = result.document || result;
            
            return `
                <div class="result-item" data-patient-id="${doc.patient_id || ''}">
                    <div class="result-header">
                        <span class="result-title">${escapeHtml(doc.title || doc.record_type || '病历记录')}</span>
                        <span class="result-score">相关度: ${(score * 100).toFixed(1)}%</span>
                    </div>
                    <div class="result-meta">
                        ${doc.patient_id ? `<span class="result-meta-item">🆔 患者ID: ${escapeHtml(doc.patient_id)}</span>` : ''}
                        ${doc.visit_time ? `<span class="result-meta-item">📅 ${formatDate(doc.visit_time)}</span>` : ''}
                        ${doc.department ? `<span class="result-meta-item">🏥 ${escapeHtml(doc.department)}</span>` : ''}
                        ${doc.record_type ? `<span class="result-meta-item">📋 ${escapeHtml(doc.record_type)}</span>` : ''}
                    </div>
                    <div class="result-content">
                        ${highlightContent(doc.content || doc.text || '', currentQuery)}
                    </div>
                    ${doc.time_score ? `<div class="time-badge" style="margin-top:0.8rem;">⏰ 时间对齐分数: ${(doc.time_score * 100).toFixed(1)}%</div>` : ''}
                    <div class="result-actions">
                        ${doc.patient_id ? `<button class="btn btn-secondary btn-sm" onclick="viewPatient('${doc.patient_id}')">查看患者详情</button>` : ''}
                        <button class="btn btn-secondary btn-sm" onclick="generateSummary('${doc.patient_id || ''}')">生成摘要</button>
                    </div>
                </div>
            `;
        }).join('');

        resultsSection.classList.remove('hidden');
        emptyState.classList.add('hidden');
    }

    // Utility functions
    function highlightContent(content, query) {
        if (!content) return '';
        
        let highlighted = escapeHtml(content.substring(0, 500));
        
        // Simple highlighting for query terms
        const terms = query.split(/\s+/).filter(t => t.length > 1);
        terms.forEach(term => {
            const regex = new RegExp(`(${escapeRegex(term)})`, 'gi');
            highlighted = highlighted.replace(regex, '<span class="result-highlight">$1</span>');
        });

        return highlighted + (content.length > 500 ? '...' : '');
    }

    function formatDate(dateStr) {
        if (!dateStr) return '';
        const date = new Date(dateStr);
        return date.toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' });
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    function escapeRegex(string) {
        return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }

    function showInfo(message) {
        infoAlert.textContent = message;
        infoAlert.classList.remove('hidden');
        setTimeout(() => infoAlert.classList.add('hidden'), 5000);
    }

    function showError(message) {
        errorAlert.textContent = message;
        errorAlert.classList.remove('hidden');
    }

    function hideAlerts() {
        infoAlert.classList.add('hidden');
        errorAlert.classList.add('hidden');
    }

    // Global functions for result actions
    window.viewPatient = function(patientId) {
        if (patientId) {
            window.location.href = `/patient.html?id=${patientId}`;
        }
    };

    window.generateSummary = function(patientId) {
        if (patientId) {
            window.location.href = `/summary.html?patient_id=${patientId}`;
        } else {
            window.location.href = '/summary.html';
        }
    };
});
