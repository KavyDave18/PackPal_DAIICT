document.addEventListener('DOMContentLoaded', async function() {
    // Initialize alerts array
    let alerts = [];
    
    // Load alerts from API
    try {
        const response = await API.Alerts.getAll();
        
        if (response.alerts && response.alerts.length > 0) {
            // Map API alerts to our format
            alerts = response.alerts.map(alert => ({
                id: alert.id.toString(),
                type: determineAlertType(alert.message),
                message: alert.message,
                time: formatAlertTime(new Date()),
                read: alert.read
            }));
        }
    } catch (error) {
        console.error('Error loading alerts:', error);
        
        // Use sample data as fallback
        alerts = [
            {
                id: '1',
                type: 'conflict',
                message: 'Conflict detected: Sarah and Mike both assigned to bring Cooking Supplies',
                time: '10 minutes ago',
                read: false
            },
            {
                id: '2',
                type: 'update',
                message: 'Mike marked Sleeping Bag as packed',
                time: '1 hour ago',
                read: false
            },
            {
                id: '3',
                type: 'new-item',
                message: 'Sarah added Camping Tent to the checklist',
                time: '3 hours ago',
                read: false
            },
            {
                id: '4',
                type: 'member-added',
                message: 'Lisa Brown joined the group',
                time: '5 hours ago',
                read: false
            },
            {
                id: '5',
                type: 'update',
                message: 'John marked First Aid Kit as delivered',
                time: '1 day ago',
                read: true
            },
            {
                id: '6',
                type: 'conflict',
                message: 'Deadline approaching: Trip Essentials due in 2 days',
                time: '1 day ago',
                read: true
            },
            {
                id: '7',
                type: 'new-item',
                message: 'Mike added Hiking Boots to the checklist',
                time: '2 days ago',
                read: true
            }
        ];
    }
    
    // Helper function to determine alert type from message
    function determineAlertType(message) {
        if (message.includes('Conflict') || message.includes('deadline') || message.includes('Deadline')) {
            return 'conflict';
        } else if (message.includes('marked') || message.includes('updated')) {
            return 'update';
        } else if (message.includes('added') && !message.includes('joined')) {
            return 'new-item';
        } else if (message.includes('joined')) {
            return 'member-added';
        }
        return 'update'; // Default type
    }
    
    // Helper function to format alert time
    function formatAlertTime(date) {
        const now = new Date();
        const diffMinutes = Math.floor((now - date) / (1000 * 60));
        
        if (diffMinutes < 60) {
            return `${diffMinutes} minutes ago`;
        } else if (diffMinutes < 24 * 60) {
            const hours = Math.floor(diffMinutes / 60);
            return `${hours} hour${hours > 1 ? 's' : ''} ago`;
        } else {
            const days = Math.floor(diffMinutes / (60 * 24));
            return `${days} day${days > 1 ? 's' : ''} ago`;
        }
    }
    
    // Get alerts container
    const alertsList = document.getElementById('alerts-list');
    
    // Get mark all read button
    const markAllReadBtn = document.getElementById('mark-all-read-btn');
    
    // Render alerts
    renderAlerts();
    
    // Mark all as read
    if (markAllReadBtn) {
        markAllReadBtn.addEventListener('click', async function() {
            try {
                // Mark all alerts as read in UI
                alerts.forEach(alert => {
                    alert.read = true;
                });
                
                // Re-render alerts
                renderAlerts();
                
                // Update notification badge
                updateNotificationBadge();
                
                // For each unread alert, call the API to mark as read
                const markReadPromises = alerts.map(alert => 
                    API.Alerts.markAsRead(alert.id)
                );
                
                // Wait for all API calls to complete
                await Promise.all(markReadPromises);
            } catch (error) {
                console.error('Error marking alerts as read:', error);
            }
        });
    }
    
    // Render alerts function
    function renderAlerts() {
        if (!alertsList) return;
        
        // Clear container
        alertsList.innerHTML = '';
        
        if (alerts.length === 0) {
            alertsList.innerHTML = `
                <div class="alerts-empty">
                    <i class="fas fa-bell"></i>
                    <h3>No notifications</h3>
                    <p>You're all caught up!</p>
                </div>
            `;
            return;
        }
        
        // Render alerts
        alerts.forEach(alert => {
            const alertItem = document.createElement('div');
            alertItem.className = `alert-item ${alert.read ? '' : 'unread'}`;
            alertItem.dataset.id = alert.id;
            
            // Get icon class based on type
            let iconClass = '';
            
            switch (alert.type) {
                case 'conflict':
                    iconClass = 'alert-icon-conflict fa-exclamation-circle';
                    break;
                case 'update':
                    iconClass = 'alert-icon-update fa-check-circle';
                    break;
                case 'new-item':
                    iconClass = 'alert-icon-new-item fa-box';
                    break;
                case 'member-added':
                    iconClass = 'alert-icon-member-added fa-user-plus';
                    break;
            }
            
            alertItem.innerHTML = `
                <div class="alert-icon ${alert.type}">
                    <i class="fas ${iconClass}"></i>
                </div>
                <div class="alert-content">
                    <div class="alert-message">${alert.message}</div>
                    <div class="alert-time"><i class="fas fa-clock"></i> ${alert.time}</div>
                </div>
                ${alert.read ? '' : '<div class="alert-unread-indicator"></div>'}
            `;
            
            alertsList.appendChild(alertItem);
            
            // Add click event to mark as read
            if (!alert.read) {
                alertItem.addEventListener('click', async function() {
                    const alertId = this.dataset.id;
                    
                    // Find alert
                    const alertIndex = alerts.findIndex(a => a.id === alertId);
                    
                    if (alertIndex !== -1) {
                        try {
                            // Mark as read in UI
                            alerts[alertIndex].read = true;
                            
                            // Re-render alerts
                            renderAlerts();
                            
                            // Update notification badge
                            updateNotificationBadge();
                            
                            // Call API to mark as read
                            await API.Alerts.markAsRead(alertId);
                        } catch (error) {
                            console.error('Error marking alert as read:', error);
                            
                            // Revert to unread if API call fails
                            alerts[alertIndex].read = false;
                            renderAlerts();
                            updateNotificationBadge();
                        }
                    }
                });
            }
        });
        
        // Update notification badge
        updateNotificationBadge();
    }
    
    // Update notification badge
    function updateNotificationBadge() {
        const unreadCount = alerts.filter(alert => !alert.read).length;
        const notificationBadges = document.querySelectorAll('.notification-badge');
        const alertCountBadge = document.querySelector('.alert-count-badge');
        
        // Update notification badges
        notificationBadges.forEach(badge => {
            badge.textContent = unreadCount;
            badge.style.display = unreadCount > 0 ? 'flex' : 'none';
        });
        
        // Update alert count badge
        if (alertCountBadge) {
            alertCountBadge.textContent = `${unreadCount} new`;
            alertCountBadge.style.display = unreadCount > 0 ? 'flex' : 'none';
        }
        
        // Update mark all read button
        if (markAllReadBtn) {
            markAllReadBtn.disabled = unreadCount === 0;
        }
    }
});