// Charles Log Dashboard JavaScript

// Function to initialize all charts
function initializeCharts(data) {
    initializeStatusCodeChart(data.statusCodes);
    initializeRequestMethodsChart(data.requestMethods);
    initializeTopHostsChart(data.topHosts);
    initializeTimingChart(data.timing);
    
    if (data.durationDistribution) {
        initializeDurationDistributionChart(data.durationDistribution);
    }
}

// Chart for status codes
function initializeStatusCodeChart(statusCodes) {
    if (!statusCodes || Object.keys(statusCodes).length === 0) return;
    
    const ctx = document.getElementById('statusCodeChart').getContext('2d');
    
    // Group status codes by category
    const categories = {
        '1xx': { count: 0, color: 'rgba(108, 117, 125, 0.7)' },  // Informational - gray
        '2xx': { count: 0, color: 'rgba(40, 167, 69, 0.7)' },    // Success - green
        '3xx': { count: 0, color: 'rgba(23, 162, 184, 0.7)' },   // Redirection - cyan
        '4xx': { count: 0, color: 'rgba(255, 193, 7, 0.7)' },    // Client Error - yellow
        '5xx': { count: 0, color: 'rgba(220, 53, 69, 0.7)' },    // Server Error - red
        'other': { count: 0, color: 'rgba(108, 117, 125, 0.7)' } // Other - gray
    };
    
    // Detailed status codes
    const detailedData = [];
    const detailedLabels = [];
    const detailedColors = [];
    
    // Process status codes
    Object.entries(statusCodes).forEach(([status, count]) => {
        if (status.match(/^1\d\d$/)) {
            categories['1xx'].count += count;
        } else if (status.match(/^2\d\d$/)) {
            categories['2xx'].count += count;
        } else if (status.match(/^3\d\d$/)) {
            categories['3xx'].count += count;
        } else if (status.match(/^4\d\d$/)) {
            categories['4xx'].count += count;
        } else if (status.match(/^5\d\d$/)) {
            categories['5xx'].count += count;
        } else {
            categories['other'].count += count;
        }
        
        // Add to detailed data
        detailedData.push(count);
        detailedLabels.push(status);
        
        // Set color based on status code category
        let color = categories['other'].color;
        if (status.match(/^1\d\d$/)) color = categories['1xx'].color;
        else if (status.match(/^2\d\d$/)) color = categories['2xx'].color;
        else if (status.match(/^3\d\d$/)) color = categories['3xx'].color;
        else if (status.match(/^4\d\d$/)) color = categories['4xx'].color;
        else if (status.match(/^5\d\d$/)) color = categories['5xx'].color;
        
        detailedColors.push(color);
    });
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: detailedLabels,
            datasets: [{
                label: 'Status Codes',
                data: detailedData,
                backgroundColor: detailedColors,
                borderColor: detailedColors.map(c => c.replace('0.7', '1')),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: true,
                    text: 'Status Code Distribution'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const value = context.raw;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `Count: ${value} (${percentage}%)`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Count'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Status Code'
                    }
                }
            }
        }
    });
}

// Chart for request methods
function initializeRequestMethodsChart(methods) {
    if (!methods || Object.keys(methods).length === 0) return;
    
    const ctx = document.getElementById('requestMethodsChart').getContext('2d');
    
    const methodColors = {
        'GET': 'rgba(23, 162, 184, 0.7)',
        'POST': 'rgba(40, 167, 69, 0.7)',
        'PUT': 'rgba(255, 193, 7, 0.7)',
        'DELETE': 'rgba(220, 53, 69, 0.7)',
        'PATCH': 'rgba(111, 66, 193, 0.7)',
        'HEAD': 'rgba(108, 117, 125, 0.7)',
        'OPTIONS': 'rgba(0, 123, 255, 0.7)'
    };
    
    const labels = Object.keys(methods);
    const data = Object.values(methods);
    const colors = labels.map(method => methodColors[method] || 'rgba(108, 117, 125, 0.7)');
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors,
                borderColor: colors.map(c => c.replace('0.7', '1')),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right'
                },
                title: {
                    display: true,
                    text: 'Request Methods'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const value = context.raw;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${context.label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

// Chart for top hosts
function initializeTopHostsChart(hosts) {
    if (!hosts || Object.keys(hosts).length === 0) return;
    
    const ctx = document.getElementById('topHostsChart').getContext('2d');
    
    // Get top 10 hosts by count
    const sortedHosts = Object.entries(hosts)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 10);
    
    const labels = sortedHosts.map(item => item[0]);
    const data = sortedHosts.map(item => item[1]);
    
    // Generate colors
    const colors = Array(labels.length).fill().map((_, i) => 
        `hsl(${(i * 360 / labels.length) % 360}, 70%, 60%, 0.7)`
    );
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Request Count',
                data: data,
                backgroundColor: colors,
                borderColor: colors.map(c => c.replace('0.7', '1')),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: true,
                    text: 'Top 10 Hosts'
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Request Count'
                    }
                }
            }
        }
    });
}

// Chart for timing metrics
function initializeTimingChart(timing) {
    if (!timing) return;
    
    const ctx = document.getElementById('timingChart').getContext('2d');
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Minimum', 'Average', 'Maximum'],
            datasets: [{
                label: 'Duration (ms)',
                data: [timing.min, timing.avg, timing.max],
                backgroundColor: [
                    'rgba(40, 167, 69, 0.7)',
                    'rgba(23, 162, 184, 0.7)',
                    'rgba(220, 53, 69, 0.7)'
                ],
                borderColor: [
                    'rgba(40, 167, 69, 1)',
                    'rgba(23, 162, 184, 1)',
                    'rgba(220, 53, 69, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: true,
                    text: 'Request Duration'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Duration (ms)'
                    }
                }
            }
        }
    });
}

// Chart for duration distribution
function initializeDurationDistributionChart(distribution) {
    if (!distribution || distribution.length === 0) return;
    
    const ctx = document.getElementById('durationDistributionChart').getContext('2d');
    
    // Convert the data into time ranges
    const ranges = ['0-100ms', '100-500ms', '500ms-1s', '1s-3s', '3s-5s', '5s+'];
    const counts = [0, 0, 0, 0, 0, 0];
    
    distribution.forEach(duration => {
        if (duration < 100) counts[0]++;
        else if (duration < 500) counts[1]++;
        else if (duration < 1000) counts[2]++;
        else if (duration < 3000) counts[3]++;
        else if (duration < 5000) counts[4]++;
        else counts[5]++;
    });
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ranges,
            datasets: [{
                label: 'Number of Requests',
                data: counts,
                backgroundColor: 'rgba(54, 162, 235, 0.7)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: true,
                    text: 'Request Duration Distribution'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Requests'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Duration Range'
                    }
                }
            }
        }
    });
} 