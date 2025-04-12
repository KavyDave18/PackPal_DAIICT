document.addEventListener('DOMContentLoaded', async function() {
    // Initialize members array
    let members = [];
    
    // Load members from API
    try {
        const response = await API.Members.getAll();
        
        if (response.members && response.members.length > 0) {
            // Map API members to our format
            members = response.members.map(member => {
                // Generate initials from name
                const nameParts = member.username.split(' ');
                let initials = '';
                
                if (nameParts.length >= 2) {
                    initials = nameParts[0][0] + nameParts[1][0];
                } else {
                    initials = nameParts[0].substring(0, 2);
                }
                
                initials = initials.toUpperCase();
                
                return {
                    id: member.id.toString(),
                    name: member.username,
                    email: member.email,
                    role: member.role || 'Member',
                    initials: initials
                };
            });
        }
    } catch (error) {
        console.error('Error loading members:', error);
        
        // Use sample data as fallback
        members = [
            {
                id: '1',
                name: 'John Doe',
                email: 'john@example.com',
                role: 'Owner',
                initials: 'JD'
            },
            {
                id: '2',
                name: 'Sarah Smith',
                email: 'sarah@example.com',
                role: 'Admin',
                initials: 'SS'
            },
            {
                id: '3',
                name: 'Mike Johnson',
                email: 'mike@example.com',
                role: 'Member',
                initials: 'MJ'
            },
            {
                id: '4',
                name: 'Lisa Brown',
                email: 'lisa@example.com',
                role: 'Member',
                initials: 'LB'
            },
            {
                id: '5',
                name: 'David Wilson',
                email: 'david@example.com',
                role: 'Viewer',
                initials: 'DW'
            }
        ];
    }
    
    // Get members container
    const membersGrid = document.getElementById('members-grid');
    
    // Render members
    renderMembers();
    
    // Add member modal
    const addMemberBtn = document.getElementById('add-member-btn');
    const addMemberModal = document.getElementById('add-member-modal');
    const addMemberClose = document.getElementById('add-member-close');
    const addMemberCancel = document.getElementById('add-member-cancel');
    const addMemberSubmit = document.getElementById('add-member-submit');
    const addMemberForm = document.getElementById('add-member-form');
    
    // Show add member modal
    if (addMemberBtn && addMemberModal) {
        addMemberBtn.addEventListener('click', function() {
            addMemberModal.classList.add('show');
        });
    }
    
    // Close add member modal
    if (addMemberClose) {
        addMemberClose.addEventListener('click', function() {
            addMemberModal.classList.remove('show');
        });
    }
    
    if (addMemberCancel) {
        addMemberCancel.addEventListener('click', function() {
            addMemberModal.classList.remove('show');
        });
    }
    
    // Close modal when clicking outside
    window.addEventListener('click', function(e) {
        if (e.target === addMemberModal) {
            addMemberModal.classList.remove('show');
        }
    });
    
    // Add new member
    if (addMemberSubmit && addMemberForm) {
        addMemberSubmit.addEventListener('click', function() {
            const nameInput = document.getElementById('member-name');
            const emailInput = document.getElementById('member-email');
            const roleInput = document.getElementById('member-role');
            
            if (!nameInput.value.trim() || !emailInput.value.trim()) {
                alert('Please enter both name and email');
                return;
            }
            
            // Generate initials from name
            const nameParts = nameInput.value.trim().split(' ');
            let initials = '';
            
            if (nameParts.length >= 2) {
                initials = nameParts[0][0] + nameParts[1][0];
            } else {
                initials = nameParts[0].substring(0, 2);
            }
            
            initials = initials.toUpperCase();
            
            const newMember = {
                id: Date.now().toString(),
                name: nameInput.value.trim(),
                email: emailInput.value.trim(),
                role: roleInput.value,
                initials: initials
            };
            
            // Add to members array
            members.push(newMember);
            
            // Re-render members
            renderMembers();
            
            // Reset form
            addMemberForm.reset();
            
            // Close modal
            addMemberModal.classList.remove('show');
        });
    }
    
    // Render members function
    function renderMembers() {
        if (!membersGrid) return;
        
        // Clear container
        membersGrid.innerHTML = '';
        
        if (members.length === 0) {
            membersGrid.innerHTML = `
                <div class="members-empty">
                    <i class="fas fa-users"></i>
                    <h3>No team members</h3>
                    <p>Add team members to collaborate on your checklists</p>
                </div>
            `;
            return;
        }
        
        // Render members
        members.forEach(member => {
            const memberCard = document.createElement('div');
            memberCard.className = 'card member-card';
            memberCard.dataset.id = member.id;
            
            // Get avatar and badge classes based on role
            let avatarClass = '';
            let badgeClass = '';
            
            switch (member.role) {
                case 'Owner':
                    avatarClass = 'avatar-owner';
                    badgeClass = 'badge-owner';
                    break;
                case 'Admin':
                    avatarClass = 'avatar-admin';
                    badgeClass = 'badge-admin';
                    break;
                case 'Member':
                    avatarClass = 'avatar-member';
                    badgeClass = 'badge-member';
                    break;
                case 'Viewer':
                    avatarClass = 'avatar-viewer';
                    badgeClass = 'badge-viewer';
                    break;
            }
            
            memberCard.innerHTML = `
                <div class="member-header">
                    <div class="member-avatar ${avatarClass}">${member.initials}</div>
                    <div class="member-info">
                        <div class="member-name">${member.name}</div>
                        <div class="member-email"><i class="fas fa-envelope"></i> ${member.email}</div>
                        <div class="member-badge badge ${badgeClass}">${member.role}</div>
                    </div>
                </div>
                <div class="member-actions">
                    <div class="member-dropdown">
                        <button class="member-dropdown-btn">
                            <i class="fas fa-ellipsis-h"></i>
                        </button>
                        <div class="member-dropdown-menu">
                            <a href="#" class="member-dropdown-item delete-member" data-id="${member.id}">
                                <i class="fas fa-trash-alt"></i> Remove
                            </a>
                        </div>
                    </div>
                </div>
            `;
            
            membersGrid.appendChild(memberCard);
        });
        
        // Add event listeners to new elements
        addMemberEventListeners();
    }
    
    // Add event listeners to member elements
    function addMemberEventListeners() {
        // Member dropdown toggles
        const dropdownToggles = document.querySelectorAll('.member-dropdown-btn');
        
        // Delete member buttons
        const deleteButtons = document.querySelectorAll('.delete-member');
        
        // Add event listeners to dropdown toggles
        dropdownToggles.forEach(toggle => {
            toggle.addEventListener('click', function(e) {
                e.stopPropagation();
                
                const dropdown = this.nextElementSibling;
                
                // Close all other dropdowns
                document.querySelectorAll('.member-dropdown-menu.show').forEach(menu => {
                    if (menu !== dropdown) {
                        menu.classList.remove('show');
                    }
                });
                
                dropdown.classList.toggle('show');
            });
        });
        
        // Add event listeners to delete buttons
        deleteButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                
                const memberId = this.dataset.id;
                
                // Confirm delete
                if (confirm('Are you sure you want to remove this member?')) {
                    // Remove member from array
                    const memberIndex = members.findIndex(member => member.id === memberId);
                    
                    if (memberIndex !== -1) {
                        members.splice(memberIndex, 1);
                        
                        // Re-render members
                        renderMembers();
                    }
                }
            });
        });
        
        // Close dropdowns when clicking outside
        document.addEventListener('click', function() {
            document.querySelectorAll('.member-dropdown-menu.show').forEach(menu => {
                menu.classList.remove('show');
            });
        });
    }
});