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
        this.targetEndTime = null;
        
        // Wall-clock listeners for tab visibility and focus
        this.handleVisibility = () => {
            if (this.isRunning && !document.hidden) {
                this.tick();
            }
        };
        document.addEventListener('visibilitychange', this.handleVisibility);
        window.addEventListener('focus', this.handleVisibility);

        this.updateDisplay();
    }
    
    start() {
        if (this.isRunning) return;
        this.isRunning = true;
        this.targetEndTime = Date.now() + (this.remainingSeconds * 1000);
        
        this.interval = setInterval(() => {
            this.tick();
        }, 1000);
    }

    tick() {
        if (!this.isRunning || !this.targetEndTime) return;
        this.remainingSeconds = Math.max(0, Math.round((this.targetEndTime - Date.now()) / 1000));
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
    }
    
    pause() {
        if (!this.isRunning) return;
        this.isRunning = false;
        clearInterval(this.interval);
        if (this.targetEndTime) {
            this.remainingSeconds = Math.max(0, Math.round((this.targetEndTime - Date.now()) / 1000));
        }
    }
    
    resume() {
        if (!this.isRunning && this.remainingSeconds > 0) {
            this.start();
        }
    }
    
    stop() {
        this.isRunning = false;
        clearInterval(this.interval);
        this.targetEndTime = null;
    }
    
    getElapsed() {
        return this.totalSeconds - this.remainingSeconds;
    }
    
    updateDisplay() {
        if (!this.element) return;
        if (typeof formatSeconds === 'function') {
            this.element.textContent = formatSeconds(this.remainingSeconds);
        } else {
            const mins = Math.floor(this.remainingSeconds / 60).toString().padStart(2, '0');
            const secs = (this.remainingSeconds % 60).toString().padStart(2, '0');
            this.element.textContent = `${mins}:${secs}`;
        }
    }
    
    checkWarnings() {
        if (!this.element) return;
        
        if (this.remainingSeconds <= 60) {
            this.element.classList.remove('badge-warning');
            this.element.classList.add('badge-danger');
            this.element.style.animation = 'pulse 1s infinite';
            this.element.dispatchEvent(new CustomEvent('timer-warning', { detail: { level: 'red' } }));
        } else if (this.remainingSeconds <= 120) {
            this.element.classList.remove('badge-primary');
            this.element.classList.add('badge-warning');
            this.element.dispatchEvent(new CustomEvent('timer-warning', { detail: { level: 'amber' } }));
        }
    }
}

window.TaskTimer = TaskTimer;
