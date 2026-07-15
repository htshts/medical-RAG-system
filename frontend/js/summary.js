/**
 * Medical RAG System - Summary Generation Page Logic
 */

document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const patientIdInput = document.getElementById('patientIdInput');
    const summaryType = document.getElementById('summaryType');
    const sectionsCheckboxes = document.getElementById('sectionsCheckboxes');
    const timeWindowInput = document.getElementById('timeWindowInput');
    const generateBtn = document.getElementById('generateBtn');
    const loadingEl = document.getElementById('loading');
    const resultSection = document.getElementById('resultSection');
    const infoAlert = document.getElementById('infoAlert');
    const errorAlert = document.getElementById('errorAlert');

    // State
    let currentSummary = null;

    // Initialize
    init();

    function init() {
        // Check URL params
        const urlParams = new URLSearchParams(window.location.search);
        const patientId = urlParams.get('patient_id');
        
        if (patientId) {
            patientIdInput.value = patientId;
        }

        // Generate button handler
        generateBtn.addEventListener('click', generateSummary);

        // Auto-generate if patient ID is provided
        if (patientId) {
            generateSummary();
        }
    }

    async function generateSummary() {
        const patientId = patientIdInput.value.trim();
        
        if (!patientId) {
            showError('请输入患者ID');
            return;
        }

        // Get selected sections
        const selectedSections = [];
        sectionsCheckboxes.querySelectorAll('input[type="checkbox"]:checked').forEach(cb => {
            selectedSections.push(cb.value);
        });

        // Show loading
        loadingEl.classList.add('active');
        resultSection.classList.add('hidden');
        generateBtn.disabled = true;
        hideAlerts();

        try {
            const data = await api.generateSummary(patientId, {
                type: summaryType.value,
                sections: selectedSections,
                timeWindow: parseInt(timeWindowInput.value) || 30,
            });

            currentSummary = data;
            displaySummary(data);
        } catch (error) {
            showError(`生成摘要失败: ${error.message}`);
        } finally {
            loadingEl.classList.remove('active');
            generateBtn.disabled = false;
        }
    }

    function displaySummary(data) {
        const summary = data.summary || data;
        
        // Build HTML
        let html = `
            <div class="summary-result">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1.5rem;">
                    <h2 style="margin:0;color:var(--primary-dark);">
                        📋 ${getSummaryTypeName(summaryType.value)} - ${escapeHtml(patientIdInput.value)}
                    </h2>
                    <button class="btn btn-secondary" onclick="window.print()">打印</button>
                </div>
        `;

        // Sections
        const sectionIcons = {
            chief_complaint: '🗣️',
            history: '📜',
            examination: '🔍',
            auxiliary_examination: '🧪',
            diagnosis: '🏷️',
            treatment: '💊',
        };

        const sectionNames = {
            chief_complaint: '主诉',
            history: '现病史',
            examination: '体格检查',
            auxiliary_examination: '辅助检查',
            diagnosis: '诊断',
            treatment: '治疗方案',
        };

        if (summary.sections) {
            Object.entries(summary.sections).forEach(([key, value]) => {
                if (value && value.text) {
                    html += `
                        <div class="summary-section">
                            <div class="summary-section-title">
                                ${sectionIcons[key] || '📌'} ${sectionNames[key] || key}
                            </div>
                            <div class="summary-text">${formatText(value.text)}</div>
                        </div>
                    `;
                }
            });
        } else if (summary.content) {
            // Fallback for simple content
            html += `
                <div class="summary-section">
                    <div class="summary-text">${formatText(summary.content)}</div>
                </div>
            `;
        }

        // Entities
        if (summary.entities) {
            html += `
                <div class="summary-section">
                    <div class="summary-section-title">🏷️ 关键实体</div>
                    <div class="entities-grid">
                        ${renderEntities(summary.entities)}
                    </div>
                </div>
            `;
        }

        // Metadata
        if (summary.metadata) {
            html += `
                <div style="margin-top:2rem;padding-top:1rem;border-top:1px solid var(--border-color);font-size:0.85rem;color:var(--text-secondary);">
                    <div>生成时间: ${formatDate(summary.metadata.generated_at)}</div>
                    <div>模型: ${escapeHtml(summary.metadata.model || 'N/A')}</div>
                    <div>处理时间: ${summary.metadata.processing_time_ms || 0}ms</div>
                </div>
            `;
        }

        html += '</div>';
        
        resultSection.innerHTML = html;
        resultSection.classList.remove('hidden');
        
        showInfo('摘要生成成功！');
    }

    function renderEntities(entities) {
        const html = [];
        
        const entityConfig = {
            diseases: { label: '疾病', class: 'entity-disease' },
            symptoms: { label: '症状', class: 'entity-symptom' },
            medications: { label: '药物', class: 'entity-medication' },
            tests: { label: '检查', class: 'entity-test' },
        };

        Object.entries(entityConfig).forEach(([key, config]) => {
            const items = entities[key] || [];
            if (items.length > 0) {
                items.forEach(item => {
                    html.push(`<span class="entity-tag ${config.class}">${escapeHtml(item.name || item)}</span>`);
                });
            }
        });

        return html.join('');
    }

    function formatText(text) {
        if (!text) return '';
        
        // Convert newlines to <br>
        return escapeHtml(text).replace(/\n/g, '<br>');
    }

    function getSummaryTypeName(type) {
        const names = {
            transfer: '转院摘要',
            discharge: '出院小结',
            admission: '入院记录',
            progress: '病程记录',
        };
        return names[type] || type;
    }

    // Utility functions
    function formatDate(dateStr) {
        if (!dateStr) return 'N/A';
        const date = new Date(dateStr);
        return date.toLocaleString('zh-CN');
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
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
});
