/**
 * CodeMirror Initialization
 */

const baseConfig = {
    theme: 'monokai',
    lineNumbers: true,
    matchBrackets: true,
    autoCloseBrackets: true,
    indentUnit: 4,
    tabSize: 4,
    viewportMargin: Infinity
};

function initSQLEditor(elementId) {
    const textArea = document.getElementById(elementId);
    if (!textArea) return null;
    
    const editor = CodeMirror.fromTextArea(textArea, {
        ...baseConfig,
        mode: 'text/x-sql',
        extraKeys: {
            'Ctrl-Enter': function(cm) {
                document.getElementById('btn-run')?.click();
            },
            'Ctrl-Shift-Enter': function(cm) {
                document.getElementById('btn-submit')?.click();
            }
        }
    });
    
    setupAutoSave(editor, elementId);
    return editor;
}

function initPythonEditor(elementId) {
    const textArea = document.getElementById(elementId);
    if (!textArea) return null;
    
    const editor = CodeMirror.fromTextArea(textArea, {
        ...baseConfig,
        mode: 'python',
        extraKeys: {
            'Ctrl-Enter': function(cm) {
                document.getElementById('btn-run')?.click();
            },
            'Ctrl-Shift-Enter': function(cm) {
                document.getElementById('btn-submit')?.click();
            }
        }
    });
    
    setupAutoSave(editor, elementId);
    return editor;
}

function setupAutoSave(editor, id) {
    const storageKey = `editor_${id}_autosave`;
    
    // Restore
    const saved = sessionStorage.getItem(storageKey);
    if (saved && !editor.getValue()) {
        editor.setValue(saved);
    }
    
    // Auto-save every 10 seconds
    setInterval(() => {
        sessionStorage.setItem(storageKey, editor.getValue());
    }, 10000);
}

window.initSQLEditor = initSQLEditor;
window.initPythonEditor = initPythonEditor;
