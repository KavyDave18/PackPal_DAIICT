document.addEventListener('DOMContentLoaded', function() {
    // Get form elements
    const signupForm = document.getElementById('signup-form');
    const nameInput = document.getElementById('name');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirm-password');
    const roleSelect = document.getElementById('role');
    const roleBadge = document.getElementById('role-badge');
    const signupButton = document.getElementById('signup-button');
    const errorMessage = document.getElementById('error-message');
    
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
    
    // Update role badge when role changes
    if (roleSelect) {
        roleSelect.addEventListener('change', function() {
            updateRoleBadge(this.value);
        });
        
        // Set initial badge
        updateRoleBadge(roleSelect.value);
    }
    
    // Function to update role badge
    function updateRoleBadge(role) {
        if (roleBadge) {
            roleBadge.textContent = role;
            
            // Reset classes
            roleBadge.className = 'badge';
            
            // Add role-specific class
            if (role === 'admin') {
                roleBadge.classList.add('admin');
            } else if (role === 'member') {
                roleBadge.classList.add('member');
            }
        }
    }
    
    // Form submission
    if (signupForm) {
        signupForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            // Reset error message
            if (errorMessage) {
                errorMessage.textContent = '';
                errorMessage.classList.remove('show');
            }
            
            // Get form data
            const name = nameInput ? nameInput.value.trim() : '';
            const email = emailInput ? emailInput.value.trim() : '';
            const password = passwordInput ? passwordInput.value.trim() : '';
            const confirmPassword = confirmPasswordInput ? confirmPasswordInput.value.trim() : '';
            const role = roleSelect ? roleSelect.value : 'member';
            
            // Validate form
            if (!name || !email || !password || !confirmPassword) {
                if (errorMessage) {
                    errorMessage.textContent = 'Please fill in all fields';
                    errorMessage.classList.add('show');
                }
                return;
            }
            
            // Email validation
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(email)) {
                if (errorMessage) {
                    errorMessage.textContent = 'Please enter a valid email address';
                    errorMessage.classList.add('show');
                }
                return;
            }
            
            // Password validation
            if (password.length < 6) {
                if (errorMessage) {
                    errorMessage.textContent = 'Password must be at least 6 characters long';
                    errorMessage.classList.add('show');
                }
                return;
            }
            
            // Confirm password
            if (password !== confirmPassword) {
                if (errorMessage) {
                    errorMessage.textContent = 'Passwords do not match';
                    errorMessage.classList.add('show');
                }
                return;
            }
            
            // Set loading state
            if (signupButton) {
                signupButton.classList.add('loading');
                signupButton.disabled = true;
            }
            
            try {
                // Prepare user data
                const userData = {
                    name: name,
                    email: email,
                    password: password,
                    role: role
                };
                
                console.log('Sending signup data:', userData);
                
                // Make direct fetch call for debugging
                const response = await fetch('http://localhost:8000/api/auth/signup', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(userData)
                });
                
                // Check for errors
                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.error || 'Signup failed');
                }
                
                // Parse response
                const data = await response.json();
                console.log('Signup successful:', data);
                
                // Store auth token and user data
                localStorage.setItem('authToken', data.token);
                localStorage.setItem('user', JSON.stringify(data.user));
                
                // Redirect to dashboard
                window.location.href = 'dashboard.html';
            } catch (error) {
                console.error('Signup error:', error);
                
                // Show error message
                if (errorMessage) {
                    errorMessage.textContent = error.message || 'Signup failed. Please try again.';
                    errorMessage.classList.add('show');
                }
                
                // Reset loading state
                if (signupButton) {
                    signupButton.classList.remove('loading');
                    signupButton.disabled = false;
                }
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