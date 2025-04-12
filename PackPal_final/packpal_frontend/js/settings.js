document.addEventListener('DOMContentLoaded', function() {
    // Settings navigation functionality
    const settingsNavItems = document.querySelectorAll('.settings-nav-item');
    const settingsSections = document.querySelectorAll('.settings-section');
    
    settingsNavItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            
            const sectionId = this.dataset.section;
            
            // Remove active class from all nav items
            settingsNavItems.forEach(navItem => navItem.classList.remove('active'));
            
            // Add active class to clicked nav item
            this.classList.add('active');
            
            // Hide all sections
            settingsSections.forEach(section => section.classList.remove('active'));
            
            // Show selected section
            document.getElementById(`${sectionId}-section`).classList.add('active');
        });
    });
    
    // Font size slider
    const fontSizeSlider = document.getElementById('font-size');
    const fontSizeValue = document.getElementById('font-size-value');
    
    if (fontSizeSlider && fontSizeValue) {
        // Update value display on slider change
        fontSizeSlider.addEventListener('input', function() {
            fontSizeValue.textContent = this.value;
        });
    }
    
    // Theme selection
    const themeOptions = document.querySelectorAll('input[name="theme"]');
    
    if (themeOptions.length > 0) {
        // Set initial value based on current theme
        const currentTheme = localStorage.getItem('theme') || 'system';
        
        document.querySelector(`input[value="${currentTheme}"]`).checked = true;
        
        // Update theme on change
        themeOptions.forEach(option => {
            option.addEventListener('change', function() {
                if (this.checked) {
                    const theme = this.value;
                    
                    if (theme === 'light') {
                        document.documentElement.classList.remove('dark');
                        localStorage.setItem('theme', 'light');
                    } else if (theme === 'dark') {
                        document.documentElement.classList.add('dark');
                        localStorage.setItem('theme', 'dark');
                    } else {
                        // System preference
                        localStorage.removeItem('theme');
                        
                        if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
                            document.documentElement.classList.add('dark');
                        } else {
                            document.documentElement.classList.remove('dark');
                        }
                    }
                }
            });
        });
    }
    
    // Form submissions
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Show success message
            showToast('Settings saved successfully!', 'success');
        });
    });
    
    // Integration connect buttons
    const connectButtons = document.querySelectorAll('.integration-action .btn:not(.connected)');
    
    connectButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Change button to connected state
            this.classList.add('connected');
            this.innerHTML = '<i class="fas fa-check"></i> Connected';
            
            // Show success message
            showToast('Integration connected successfully!', 'success');
        });
    });
    
    // Toast notification function
    function showToast(message, type = 'info') {
        // Create toast element
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        
        // Add icon based on type
        let icon = '';
        
        switch (type) {
            case 'success':
                icon = '<i class="fas fa-check-circle"></i>';
                break;
            case 'error':
                icon = '<i class="fas fa-exclamation-circle"></i>';
                break;
            case 'warning':
                icon = '<i class="fas fa-exclamation-triangle"></i>';
                break;
            default:
                icon = '<i class="fas fa-info-circle"></i>';
        }
        
        toast.innerHTML = `
            ${icon}
            <span>${message}</span>
            <button class="toast-close"><i class="fas fa-times"></i></button>
        `;
        
        // Add toast to document
        document.body.appendChild(toast);
        
        // Show toast
        setTimeout(() => {
            toast.classList.add('show');
        }, 10);
        
        // Auto hide toast after 3 seconds
        setTimeout(() => {
            toast.classList.remove('show');
            
            // Remove toast from DOM after animation
            setTimeout(() => {
                document.body.removeChild(toast);
            }, 300);
        }, 3000);
        
        // Close toast on button click
        const closeBtn = toast.querySelector('.toast-close');
        
        closeBtn.addEventListener('click', function() {
            toast.classList.remove('show');
            
            // Remove toast from DOM after animation
            setTimeout(() => {
                document.body.removeChild(toast);
            }, 300);
        });
    }
});