document.addEventListener('DOMContentLoaded', function() {
    // Sample data for notifications
    const notifications = [
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
        }
    ];
    
    // Get notification elements
    const notificationBtn = document.getElementById('notification-btn');
    const notificationDropdown = document.getElementById('notification-dropdown');
    const notificationList = document.getElementById('notification-list');
    const notificationBadge = document.querySelector('.notification-badge');
    
    // Render notifications
    renderNotifications();
    
    // Toggle notification dropdown
    if (notificationBtn && notificationDropdown) {
        notificationBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            notificationDropdown.classList.toggle('show');
            
            // Close user dropdown if open
            const userDropdownMenu = document.getElementById('user-dropdown-menu');
            if (userDropdownMenu) {
                userDropdownMenu.classList.remove('show');
            }
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', function(e) {
            if (!notificationDropdown.contains(e.target) && e.target !== notificationBtn) {
                notificationDropdown.classList.remove('show');
            }
        });
    }
    
    // Render notifications function
    function renderNotifications() {
        if (!notificationList) return;
        
        // Clear container
        notificationList.innerHTML = '';
        
        if (notifications.length === 0) {
            notificationList.innerHTML = `
                <div class="notification-empty">
                    <i class="fas fa-bell-slash"></i>
                    <p>No new notifications</p>
                </div>
            `;
            return;
        }
        
        // Render notifications
        notifications.forEach(notification => {
            const notificationItem = document.createElement('div');
            notificationItem.className = `notification-item ${notification.read ? '' : 'unread'}`;
            notificationItem.dataset.id = notification.id;
            
            // Get icon class based on type
            let iconClass = '';
            
            switch (notification.type) {
                case 'conflict':
                    iconClass = 'notification-icon-conflict fa-exclamation-circle';
                    break;
                case 'update':
                    iconClass = 'notification-icon-update fa-check-circle';
                    break;
                case 'new-item':
                    iconClass = 'notification-icon-new-item fa-box';
                    break;
                case 'member-added':
                    iconClass = 'notification-icon-member-added fa-user-plus';
                    break;
            }
            
            notificationItem.innerHTML = `
                <div class="notification-icon ${notification.type}">
                    <i class="fas ${iconClass}"></i>
                </div>
                <div class="notification-content">
                    <div class="notification-message">${notification.message}</div>
                    <div class="notification-time"><i class="fas fa-clock"></i> ${notification.time}</div>
                </div>
                ${notification.read ? '' : '<div class="notification-unread-indicator"></div>'}
            `;
            
            notificationList.appendChild(notificationItem);
            
            // Add click event to mark as read
            if (!notification.read) {
                notificationItem.addEventListener('click', function() {
                    const notificationId = this.dataset.id;
                    
                    // Find notification
                    const notificationIndex = notifications.findIndex(n => n.id === notificationId);
                    
                    if (notificationIndex !== -1) {
                        // Mark as read
                        notifications[notificationIndex].read = true;
                        
                        // Re-render notifications
                        renderNotifications();
                        
                        // Update notification badge
                        updateNotificationBadge();
                    }
                });
            }
        });
        
        // Update notification badge
        updateNotificationBadge();
    }
    
    // Update notification badge
    function updateNotificationBadge() {
        const unreadCount = notifications.filter(notification => !notification.read).length;
        
        if (notificationBadge) {
            notificationBadge.textContent = unreadCount;
            notificationBadge.style.display = unreadCount > 0 ? 'flex' : 'none';
        }
    }
});