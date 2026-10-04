/**
 * Global utilities for QueryLearn
 */

document.addEventListener('DOMContentLoaded', () => {
    // Page transition
    document.body.classList.add('fade-in');

    // Enforce dark mode permanently
    initTheme();
});

function initTheme() {
    localStorage.removeItem('theme');
    document.body.setAttribute('data-theme', 'dark');
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
