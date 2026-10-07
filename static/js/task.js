/**
 * Task workspace logic
 */

let editorInstance = null;
let taskTimer = null;
let currentAttempts = 0;

document.addEventListener('DOMContentLoaded', () => {
    const editorEl = document.getElementById('code-editor');
    if (!editorEl) return;
    
    const language = editorEl.dataset.language;
    if (language === 'sql') {
        editorInstance = initSQLEditor('code-editor');
    } else if (language === 'python') {
        editorInstance = initPythonEditor('code-editor');
    }
    
    // Initialize Timer
    const timerEl = document.getElementById('task-timer');
    if (timerEl) {
        const allocated = parseInt(timerEl.dataset.allocated || 300, 10);
        taskTimer = new TaskTimer('task-timer', allocated, handleTimeout);
        taskTimer.start();
    }
    
    // Buttons
    document.getElementById('btn-run')?.addEventListener('click', runCode);
    document.getElementById('btn-submit')?.addEventListener('click', confirmSubmit);
    document.getElementById('btn-skip')?.addEventListener('click', confirmSkip);
});

async function runCode() {
    if (!editorInstance) return;
    
    const code = editorInstance.getValue().trim();
    if (!code) {
        showToast('Please enter some code to run', 'warning');
        return;
    }
    
    const runBtn = document.getElementById('btn-run');
    runBtn.disabled = true;
    runBtn.textContent = 'Running...';
    
    const resultArea = document.getElementById('result-area');
    resultArea.innerHTML = '<div class="skeleton" style="height: 100px;"></div>';
    
    try {
        const taskId = document.getElementById('task-id').value;
        const res = await fetchJSON('/api/run', {
            method: 'POST',
            body: JSON.stringify({ task_id: taskId, code: code })
        });
        
        currentAttempts++;
        document.getElementById('attempt-counter').textContent = currentAttempts;
        
        if (res.success) {
            renderResults(res.data, res.columns);
        } else {
            renderError(res.error);
        }
    } catch (err) {
        renderError(err.message);
        document.getElementById('workspace-panel').classList.add('shake');
    } finally {
        runBtn.disabled = false;
        runBtn.textContent = 'Run Code';
    }
}

function renderResults(data, columns) {
    const area = document.getElementById('result-area');
    if (!data || data.length === 0) {
        area.innerHTML = '<div class="alert alert-info">Query returned 0 rows.</div>';
        return;
    }
    
    let html = '<div style="overflow-x: auto;"><table class="table data-table"><thead><tr>';
    columns.forEach(col => {
        html += `<th>${col}</th>`;
    });
    html += '</tr></thead><tbody>';
    
    data.forEach(row => {
        html += '<tr>';
        row.forEach(val => {
            html += `<td>${val !== null ? val : '<em>null</em>'}</td>`;
        });
        html += '</tr>';
    });
    
    html += '</tbody></table></div>';
    area.innerHTML = html;
}

function renderError(msg) {
    const area = document.getElementById('result-area');
    area.innerHTML = `<div class="alert alert-danger"><pre style="white-space: pre-wrap;">${msg}</pre></div>`;
}

function confirmSubmit() {
    if (!editorInstance) return;
    
    const code = editorInstance.getValue().trim();
    if (!code) {
        showToast('Please enter some code before submitting', 'warning');
        return;
    }
    
    showModal(
        'Submit Task',
        'Are you sure you want to submit your code? You cannot change it after submission.',
        () => submitCode(code)
    );
}

async function submitCode(code) {
    const taskId = document.getElementById('task-id').value;
    const elapsed = taskTimer ? taskTimer.getElapsed() : 0;
    
    if (taskTimer) taskTimer.stop();
    
    try {
        const res = await fetchJSON('/api/submit', {
            method: 'POST',
            body: JSON.stringify({
                task_id: taskId,
                code: code,
                elapsed_seconds: elapsed,
                attempts: currentAttempts
            })
        });
        
        if (res.success) {
            showToast('Task submitted successfully!', 'success');
            setTimeout(() => {
                window.location.href = res.next_url;
            }, 1000);
        } else {
            showToast('Submission failed: ' + res.message, 'error');
            if (taskTimer) taskTimer.start();
        }
    } catch (err) {
        showToast('Error: ' + err.message, 'error');
        if (taskTimer) taskTimer.start();
    }
}

function handleTimeout() {
    showToast('Time is up! Auto-submitting your code.', 'warning');
    const code = editorInstance ? editorInstance.getValue().trim() : '';
    submitCode(code);
}

function confirmSkip() {
    showModal(
        'Skip Task',
        'Are you sure you want to skip this task? It will be recorded as failed.',
        () => {
            const code = editorInstance ? editorInstance.getValue().trim() : '';
            submitCode(code); // backend will handle skip flag if needed, or we just submit current state
        }
    );
}
