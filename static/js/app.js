/**
 * Global utilities for QueryLearn
 */

document.addEventListener('DOMContentLoaded', () => {
    // Page transition
    document.body.classList.add('fade-in');

    // Init theme
    initTheme();

    // Bind theme toggle button
    const toggleBtn = document.getElementById('theme-toggle');
    if (toggleBtn) {
        toggleBtn.addEventListener('click', toggleTheme);
    }
});

/**
 * Moon SVG (shown in dark mode — click to go light)
 * Sun SVG (shown in light mode — click to go dark)
 */
const ICON_MOON = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>';
const ICON_SUN  = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>';

function initTheme() {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.body.setAttribute('data-theme', savedTheme);
    updateToggleIcon(savedTheme);
}

function toggleTheme() {
    const currentTheme = document.body.getAttribute('data-theme') || 'dark';
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.body.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateToggleIcon(newTheme);
}

function updateToggleIcon(theme) {
    const toggleBtn = document.getElementById('theme-toggle');
    if (toggleBtn) {
        toggleBtn.innerHTML = theme === 'dark' ? ICON_MOON : ICON_SUN;
        toggleBtn.title = theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode';
    }
}

/**
 * Show a toast notification
 * @param {string} message 
 * @param {string} type - 'success', 'error', 'warning', 'info'
 * @param {number} duration - milliseconds
 */
function showToast(message, type = 'success', duration = 3000) {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideInRight 0.3s reverse forwards';
        setTimeout(() => {
            if (document.body.contains(toast)) {
                document.body.removeChild(toast);
            }
        }, 300);
    }, duration);
}

/**
 * Modal System
 */
const modalSystem = {
    showModal: function(title, bodyHTML, onConfirm) {
        let modal = document.getElementById('app-modal');
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'app-modal';
            modal.className = 'modal';
            modal.innerHTML = `
                <div class="modal-content slide-in">
                    <h3 id="modal-title"></h3>
                    <div id="modal-body" style="margin: 1rem 0;"></div>
                    <div style="display: flex; justify-content: flex-end; gap: 1rem; margin-top: 1.5rem;">
                        <button class="btn btn-outline" id="modal-cancel">Cancel</button>
                        <button class="btn btn-primary" id="modal-confirm">Confirm</button>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);
            
            document.getElementById('modal-cancel').addEventListener('click', this.hideModal);
        }
        
        document.getElementById('modal-title').textContent = title;
        document.getElementById('modal-body').innerHTML = bodyHTML;
        
        const confirmBtn = document.getElementById('modal-confirm');
        const newConfirmBtn = confirmBtn.cloneNode(true);
        confirmBtn.parentNode.replaceChild(newConfirmBtn, confirmBtn);
        
        newConfirmBtn.addEventListener('click', () => {
            if (onConfirm) onConfirm();
            this.hideModal();
        });
        
        modal.style.display = 'flex';
    },
    
    hideModal: function() {
        const modal = document.getElementById('app-modal');
        if (modal) {
            modal.style.display = 'none';
        }
    }
};

window.showModal = modalSystem.showModal.bind(modalSystem);
window.hideModal = modalSystem.hideModal.bind(modalSystem);

/**
 * AJAX Helper
 */
async function fetchJSON(url, options = {}) {
    try {
        const response = await fetch(url, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                ...(options.headers || {})
            }
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || data.message || 'Request failed');
        }
        
        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

/**
 * Format seconds to MM:SS
 */
function formatSeconds(seconds) {
    const m = Math.floor(seconds / 60).toString().padStart(2, '0');
    const s = (seconds % 60).toString().padStart(2, '0');
    return `${m}:${s}`;
}
