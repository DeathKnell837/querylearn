/**
 * Countdown timer for tasks
 */
class TaskTimer {
    constructor(elementId, totalSeconds, onComplete) {
        this.element = document.getElementById(elementId);
        this.totalSeconds = totalSeconds;
        this.remainingSeconds = totalSeconds;
        this.onComplete = onComplete;
        this.interval = null;
        this.isRunning = false;
        
        this.updateDisplay();
    }
    
    start() {
        if (this.isRunning) return;
        this.isRunning = true;
        
        this.interval = setInterval(() => {
            this.remainingSeconds--;
            this.updateDisplay();
            this.checkWarnings();
            
            if (this.remainingSeconds <= 0) {
                this.stop();
                if (this.element) {
                    this.element.dispatchEvent(new CustomEvent('timer-expired'));
                }
                if (typeof this.onComplete === 'function') {
                    this.onComplete();
                }
            }
        }, 1000);
    }
    
    pause() {
        if (!this.isRunning) return;
        this.isRunning = false;
        clearInterval(this.interval);
    }
    
    resume() {
        if (!this.isRunning && this.remainingSeconds > 0) {
            this.start();
        }
    }
    
    stop() {
        this.isRunning = false;
        clearInterval(this.interval);
    }
    
    getElapsed() {
        return this.totalSeconds - this.remainingSeconds;
    }
    
    updateDisplay() {
        if (!this.element) return;
        this.element.textContent = formatSeconds(this.remainingSeconds);
    }
    
    checkWarnings() {
        if (!this.element) return;
        
        if (this.remainingSeconds === 120) {
            this.element.classList.remove('badge-primary');
            this.element.classList.add('badge-warning');
            this.element.dispatchEvent(new CustomEvent('timer-warning', { detail: { level: 'amber' } }));
        } else if (this.remainingSeconds === 60) {
            this.element.classList.remove('badge-warning');
            this.element.classList.add('badge-danger');
            this.element.style.animation = 'pulse 1s infinite';
            this.element.dispatchEvent(new CustomEvent('timer-warning', { detail: { level: 'red' } }));
        }
    }
}

window.TaskTimer = TaskTimer;
