document.addEventListener('DOMContentLoaded', function() {
    // Get form elements
    const loginForm = document.getElementById('login-form');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    const loginButton = document.getElementById('login-button');
    const errorMessage = document.getElementById('login-error');
    
    // Toggle password visibility
    const togglePasswordButtons = document.querySelectorAll('.toggle-password');
    
    togglePasswordButtons.forEach(button => {
        button.addEventListener('click', function() {
            const input = this.previousElementSibling;
            
            // Toggle password visibility
            if (input.type === 'password') {
                input.type = 'text';
                this.classList.remove('fa-eye-slash');
                this.classList.add('fa-eye');
            } else {
                input.type = 'password';
                this.classList.remove('fa-eye');
                this.classList.add('fa-eye-slash');
            }
        });
    });
    
    // Form submission
    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            // Get form data
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            
            // Validate form
            if (!email || !password) {
                errorMessage.textContent = 'Please enter email and password';
                errorMessage.classList.add('show');
                return;
            }
            
            // Set loading state
            loginButton.classList.add('loading');
            loginButton.disabled = true;
            
            try {
                // Use our API service to login
                const response = await API.Auth.login(email, password);
                
                // Store auth token and user in localStorage
                localStorage.setItem('authToken', response.token);
                localStorage.setItem('user', JSON.stringify(response.user));
                
                // Redirect to dashboard
                window.location.href = 'dashboard.html';
            } catch (error) {
                // Clear any existing token to prevent future issues
                localStorage.removeItem('authToken');
                
                // Show error message
                console.error("Login error:", error);
                errorMessage.textContent = error.message || 'Login failed. Please try again.';
                errorMessage.classList.add('show');
                
                // Reset loading state
                loginButton.classList.remove('loading');
                loginButton.disabled = false;
            }
        });
    }
    
    // Add floating label effect
    const inputs = document.querySelectorAll('input');
    
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });
        
        input.addEventListener('blur', function() {
            if (this.value === '') {
                this.parentElement.classList.remove('focused');
            }
        });
        
        // Check if input has value on page load
        if (input.value !== '') {
            input.parentElement.classList.add('focused');
        }
    });
});