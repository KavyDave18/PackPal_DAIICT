document.addEventListener('DOMContentLoaded', async function() {
    // Initialize data counts with default values
    let toPackCount = 8;
    let packedCount = 12;
    let deliveredCount = 5;
    
    // Try to load data from API
    try {
        // Get all checklists
        const response = await API.Checklist.getAll();
        
        // Count items by status
        if (response.checklists && response.checklists.length > 0) {
            // Reset counters to recalculate from API data
            toPackCount = 0;
            packedCount = 0;
            deliveredCount = 0;
            
            response.checklists.forEach(checklist => {
                if (checklist.items && checklist.items.length > 0) {
                    checklist.items.forEach(item => {
                        if (item.checked === false) {
                            toPackCount++;
                        } else {
                            packedCount++;
                        }
                    });
                }
            });
        }
    } catch (error) {
        console.error('Error loading checklists:', error);
        // Using default values set above if API fails
    }
    
    // Initialize the status chart
    const statusChart = document.getElementById('status-chart');
    
    if (statusChart) {
        const ctx = statusChart.getContext('2d');
        
        // Chart data with API values or defaults
        const data = {
            labels: ['To Pack', 'Packed', 'Delivered'],
            datasets: [{
                data: [toPackCount, packedCount, deliveredCount],
                backgroundColor: [
                    '#94a3b8',
                    '#3b82f6',
                    '#22c55e'
                ],
                borderColor: [
                    '#94a3b8',
                    '#3b82f6',
                    '#22c55e'
                ],
                borderWidth: 2,
                hoverOffset: 15,
                borderRadius: 5,
                spacing: 5
            }]
        };
        
        // Chart options
        const options = {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '65%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        usePointStyle: true,
                        pointStyle: 'circle',
                        font: {
                            size: 12,
                            weight: 'bold'
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleFont: {
                        size: 14,
                        weight: 'bold'
                    },
                    bodyFont: {
                        size: 13
                    },
                    padding: 12,
                    cornerRadius: 8,
                    callbacks: {
                        label: function(context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = Math.round((context.raw / total) * 100);
                            return `${context.label}: ${context.raw} items (${percentage}%)`;
                        }
                    }
                }
            },
            animation: {
                animateScale: true,
                animateRotate: true,
                duration: 2000,
                easing: 'easeOutQuart',
                onComplete: function() {
                    // Add center text
                    const width = statusChart.width;
                    const height = statusChart.height;
                    const ctx = statusChart.getContext('2d');
                    
                    ctx.restore();
                    ctx.font = 'bold 16px Inter';
                    ctx.textBaseline = 'middle';
                    ctx.textAlign = 'center';
                    
                    const total = data.datasets[0].data.reduce((a, b) => a + b, 0);
                    const text = `${total} Items`;
                    
                    // Get theme
                    const isDark = document.documentElement.classList.contains('dark');
                    ctx.fillStyle = isDark ? '#f8fafc' : '#1e293b';
                    
                    ctx.fillText(text, width / 2, height / 2);
                    ctx.save();
                }
            },
            elements: {
                arc: {
                    borderWidth: 0
                }
            },
            interaction: {
                mode: 'nearest',
                intersect: true,
                axis: 'xy'
            }
        };
        
        // Create the chart
        const chart = new Chart(ctx, {
            type: 'doughnut',
            data: data,
            options: options
        });
        
        // Add hover effect to chart segments
        statusChart.addEventListener('mousemove', function(e) {
            const activePoints = chart.getElementsAtEventForMode(e, 'nearest', { intersect: true }, false);
            
            if (activePoints.length > 0) {
                statusChart.style.cursor = 'pointer';
            } else {
                statusChart.style.cursor = 'default';
            }
        });
        
        // Add click event to chart segments
        statusChart.addEventListener('click', function(e) {
            const activePoints = chart.getElementsAtEventForMode(e, 'nearest', { intersect: true }, false);
            
            if (activePoints.length > 0) {
                const clickedIndex = activePoints[0].index;
                const label = data.labels[clickedIndex];
                
                // Navigate to checklist page
                window.location.href = 'checklist.html';
            }
        });
        
        // Update chart on theme change
        const themeToggleBtn = document.getElementById('theme-toggle-btn');
        
        if (themeToggleBtn) {
            themeToggleBtn.addEventListener('click', function() {
                // Redraw chart with updated colors
                chart.update();
            });
        }
    }
    
    // Animate progress bar on load
    const progressFill = document.querySelector('.progress-fill');
    
    if (progressFill) {
        setTimeout(() => {
            progressFill.style.width = '68%';
        }, 300);
    }
    
    // Notification badge update
    const notificationBtn = document.getElementById('notification-btn');
    const notificationBadge = document.querySelector('.notification-badge');
    
    if (notificationBtn && notificationBadge) {
        notificationBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            
            // Toggle notification dropdown
            const notificationDropdown = document.getElementById('notification-dropdown');
            
            if (notificationDropdown) {
                notificationDropdown.classList.toggle('show');
                
                // Close user dropdown if open
                const userDropdownMenu = document.getElementById('user-dropdown-menu');
                if (userDropdownMenu) {
                    userDropdownMenu.classList.remove('show');
                }
            } else {
                // Navigate to alerts page if dropdown doesn't exist
                window.location.href = 'alerts.html';
            }
        });
    }
    
    // Add animation to activity items
    const activityItems = document.querySelectorAll('.activity-item');
    
    activityItems.forEach((item, index) => {
        item.style.animationDelay = `${index * 0.1}s`;
    });
    
    // Add hover effect to stats cards
    const statsCards = document.querySelectorAll('.stats-card');
    
    statsCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-10px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = '';
        });
    });
});