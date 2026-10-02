/**
 * Multi-step form wizard
 */
class FormStepper {
    constructor(formId, steps) {
        this.form = document.getElementById(formId);
        this.steps = steps; // Array of step ids
        this.currentStep = 0;
        
        if (!this.form) return;
        
        this.updateUI();
        
        // Bind next/prev buttons
        this.form.querySelectorAll('.btn-next').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                this.nextStep();
            });
        });
        
        this.form.querySelectorAll('.btn-prev').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                this.prevStep();
            });
        });
    }
    
    nextStep() {
        if (this.validateCurrentStep() && this.currentStep < this.steps.length - 1) {
            this.currentStep++;
            this.updateUI();
        }
    }
    
    prevStep() {
        if (this.currentStep > 0) {
            this.currentStep--;
            this.updateUI();
        }
    }
    
    goToStep(n) {
        if (n >= 0 && n < this.steps.length) {
            this.currentStep = n;
            this.updateUI();
        }
    }
    
    validateCurrentStep() {
        const stepId = this.steps[this.currentStep];
        const stepPanel = document.getElementById(stepId);
        if (!stepPanel) return false;
        
        const inputs = stepPanel.querySelectorAll('input[required], select[required]');
        let isValid = true;
        
        inputs.forEach(input => {
            if (!input.checkValidity()) {
                input.reportValidity();
                isValid = false;
            }
        });
        
        return isValid;
    }
    
    updateUI() {
        // Update panels
        this.steps.forEach((stepId, index) => {
            const panel = document.getElementById(stepId);
            if (panel) {
                if (index === this.currentStep) {
                    panel.style.display = 'block';
                    panel.classList.add('fade-in');
                } else {
                    panel.style.display = 'none';
                    panel.classList.remove('fade-in');
                }
            }
        });
        
        // Update stepper indicators if they exist
        const indicators = document.querySelectorAll('.stepper .step');
        indicators.forEach((indicator, index) => {
            indicator.classList.remove('active', 'completed');
            if (index < this.currentStep) {
                indicator.classList.add('completed');
                indicator.innerHTML = '✓';
            } else if (index === this.currentStep) {
                indicator.classList.add('active');
                indicator.innerHTML = (index + 1).toString();
            } else {
                indicator.innerHTML = (index + 1).toString();
            }
        });
    }
}

window.FormStepper = FormStepper;
