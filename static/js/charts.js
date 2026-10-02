/**
 * Dashboard Chart.js configurations
 */

const chartDefaults = {
    color: '#cbd5e1',
    font: {
        family: "'Inter', sans-serif"
    }
};

const gridConfig = {
    color: 'rgba(255, 255, 255, 0.05)',
    borderColor: 'rgba(255, 255, 255, 0.1)'
};

function initChartDefaults() {
    if (typeof Chart !== 'undefined') {
        Chart.defaults.color = chartDefaults.color;
        Chart.defaults.font.family = chartDefaults.font.family;
        Chart.defaults.scale.grid.color = gridConfig.color;
        Chart.defaults.scale.grid.borderColor = gridConfig.borderColor;
    }
}

function createComparisonChart(canvasId, sqlData, pythonData, labels) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels || ['Task 1', 'Task 2', 'Task 3', 'Task 4', 'Task 5', 'Task 6'],
            datasets: [
                {
                    label: 'SQL',
                    data: sqlData,
                    backgroundColor: 'rgba(59, 130, 246, 0.8)',
                    borderColor: '#3b82f6',
                    borderWidth: 1
                },
                {
                    label: 'Python (Pandas)',
                    data: pythonData,
                    backgroundColor: 'rgba(139, 92, 246, 0.8)',
                    borderColor: '#8b5cf6',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'top' }
            },
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
}

function createSuccessRateChart(canvasId, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Success', 'Failure', 'Timeout'],
            datasets: [{
                data: data,
                backgroundColor: [
                    'rgba(34, 197, 94, 0.8)', // Success
                    'rgba(239, 68, 68, 0.8)', // Failure
                    'rgba(245, 158, 11, 0.8)' // Timeout
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '70%',
            plugins: {
                legend: { position: 'right' }
            }
        }
    });
}

function createSurveyChart(canvasId, labels, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    
    new Chart(ctx, {
        type: 'radar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Average Score',
                data: data,
                backgroundColor: 'rgba(59, 130, 246, 0.2)',
                borderColor: '#3b82f6',
                pointBackgroundColor: '#3b82f6',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: '#3b82f6'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    angleLines: { color: gridConfig.color },
                    grid: { color: gridConfig.color },
                    pointLabels: { color: chartDefaults.color },
                    ticks: {
                        backdropColor: 'transparent',
                        color: chartDefaults.color,
                        min: 1,
                        max: 5,
                        stepSize: 1
                    }
                }
            }
        }
    });
}

function createTimelineChart(canvasId, labels, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Completion Time (s)',
                data: data,
                fill: true,
                backgroundColor: 'rgba(139, 92, 246, 0.2)',
                borderColor: '#8b5cf6',
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
}

function createBenchmarkChart(canvasId, labels, sqlData, pythonData) {
    // Reuses comparison chart logic essentially
    createComparisonChart(canvasId, sqlData, pythonData, labels);
}

// Export functions
window.initChartDefaults = initChartDefaults;
window.createComparisonChart = createComparisonChart;
window.createSuccessRateChart = createSuccessRateChart;
window.createSurveyChart = createSurveyChart;
window.createTimelineChart = createTimelineChart;
window.createBenchmarkChart = createBenchmarkChart;
