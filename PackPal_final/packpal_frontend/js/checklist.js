document.addEventListener('DOMContentLoaded', async function() {
    // Check for login token
    const token = localStorage.getItem('authToken');
    if (!token) {
        console.log('No authentication token found, redirecting to login');
        window.location.href = '/';
        return;
    }
    
    // Get checklist containers
    const toPackContainer = document.getElementById('to-pack-items');
    const packedContainer = document.getElementById('packed-items');
    const deliveredContainer = document.getElementById('delivered-items');
    
    // Initialize items array and checklist ID
    let items = [];
    let currentChecklistId = null;
    
    // Helper function to update items array and localStorage
    function updateItems(newItems) {
        items = newItems;
        localStorage.setItem('checklist_items', JSON.stringify(items));
        console.log(`Items updated. New count: ${items.length}`);
    }
    
    // Try to load items from localStorage first
    const savedItems = localStorage.getItem('checklist_items');
    const savedChecklistId = localStorage.getItem('current_checklist_id');
    
    if (savedItems && savedChecklistId) {
        try {
            const parsedItems = JSON.parse(savedItems);
            // Make sure we have a valid array of items
            if (Array.isArray(parsedItems)) {
                items = parsedItems;
                window.packpalItems = items; // Keep in sync
                currentChecklistId = parseInt(savedChecklistId);
                console.log(`Loaded ${items.length} items from localStorage with checklist ID ${currentChecklistId}`);
                console.log(`Item IDs:`, items.map(i => i.id).join(', '));
            } else {
                console.error("Saved items is not an array:", parsedItems);
                // Reset localStorage
                localStorage.removeItem('checklist_items');
                updateItems([]); // Reset items
            }
        } catch (e) {
            console.error("Error parsing saved items:", e);
            // Clear corrupted data
            localStorage.removeItem('checklist_items');
        }
    }
    
    // Load items from API
    try {
        console.log("Attempting to load checklists from API...");
        
        // Get all checklists
        const response = await API.Checklist.getAll();
        console.log("Checklists response:", response);
        
        // If there are checklists, get the first one's items
        if (response.checklists && response.checklists.length > 0) {
            const firstChecklist = response.checklists[0];
            currentChecklistId = firstChecklist.id;
            console.log("Using checklist ID:", currentChecklistId);
            localStorage.setItem('current_checklist_id', currentChecklistId);
            
            // If we have items from localStorage, prefer those
            if (items.length > 0) {
                console.log("Using items from localStorage instead of API");
            } 
            // If this checklist has items from API, use them only if localStorage is empty
            else if (firstChecklist.items && firstChecklist.items.length > 0) {
                // Map the API items to our format
                const apiItems = firstChecklist.items.map(item => ({
                    id: item.id.toString(), // Ensure ID is a string
                    name: item.title || item.text,
                    description: item.description || '',
                    status: item.status || (item.checked ? 'Packed' : 'To Pack'),
                    assignedTo: item.assigned_to || null,
                    category: item.category || 'General',
                    checklist_id: currentChecklistId
                }));
                
                console.log("Loaded items from API:", apiItems.length);
                console.log("Item IDs:", apiItems.map(i => i.id).join(', '));
                
                // Update items with the API data
                updateItems(apiItems);
            } else {
                console.log("No items found in checklist, keeping localStorage items");
            }
        } else {
            console.error("No checklists found in response");
        }
    } catch (error) {
        console.error('Error loading checklists:', error);
        // Don't reset items or use sample data if localStorage already has items
        if (items.length === 0) {
            console.log("Using sample data as fallback");
            items = [
        {
            id: '1',
            name: 'Tent',
            description: '4-person camping tent',
            status: 'To Pack',
            assignedTo: 'John',
            category: 'Camping'
        },
        {
            id: '2',
            name: 'Sleeping Bag',
            description: 'Warm sleeping bag for cold weather',
            status: 'Packed',
            assignedTo: 'Sarah',
            category: 'Camping'
        },
        {
            id: '3',
            name: 'First Aid Kit',
            description: 'Basic first aid supplies',
            status: 'Packed',
            assignedTo: 'Mike',
            category: 'Safety'
        },
        {
            id: '4',
            name: 'Cooking Stove',
            description: 'Portable camping stove',
            status: 'Delivered',
            assignedTo: 'Lisa',
            category: 'Cooking'
        },
        {
            id: '5',
            name: 'Water Filter',
            description: 'Portable water filtration system',
            status: 'To Pack',
            assignedTo: null,
            category: 'Safety'
        },
        {
            id: '6',
            name: 'Hiking Boots',
            description: 'Waterproof hiking boots',
            status: 'Packed',
            assignedTo: 'John',
            category: 'Clothing'
        },
        {
            id: '7',
            name: 'Flashlight',
            description: 'LED flashlight with extra batteries',
            status: 'Delivered',
            assignedTo: 'Sarah',
            category: 'Equipment'
        },
        {
            id: '8',
            name: 'Cooler',
            description: 'Large cooler for food storage',
            status: 'To Pack',
            assignedTo: 'Mike',
            category: 'Food'
        }
    ];
            updateItems(items);
        }
    }
    
    // Render items
    renderItems();
    
    // Add item modal
    const addItemBtn = document.getElementById('add-item-btn');
    const addItemModal = document.getElementById('add-item-modal');
    const addItemClose = document.getElementById('add-item-close');
    const addItemCancel = document.getElementById('add-item-cancel');
    const addItemSubmit = document.getElementById('add-item-submit');
    const addItemForm = document.getElementById('add-item-form');
    
    // Edit item modal
    const editItemModal = document.getElementById('edit-item-modal');
    const editItemClose = document.getElementById('edit-item-close');
    const editItemCancel = document.getElementById('edit-item-cancel');
    const editItemSubmit = document.getElementById('edit-item-submit');
    const editItemForm = document.getElementById('edit-item-form');
    
    // Show add item modal
    if (addItemBtn && addItemModal) {
        addItemBtn.addEventListener('click', function() {
            addItemModal.classList.add('show');
        });
    }
    
    // Close add item modal
    if (addItemClose) {
        addItemClose.addEventListener('click', function() {
            addItemModal.classList.remove('show');
        });
    }
    
    if (addItemCancel) {
        addItemCancel.addEventListener('click', function() {
            addItemModal.classList.remove('show');
        });
    }
    
    // Close edit item modal
    if (editItemClose) {
        editItemClose.addEventListener('click', function() {
            editItemModal.classList.remove('show');
        });
    }
    
    if (editItemCancel) {
        editItemCancel.addEventListener('click', function() {
            editItemModal.classList.remove('show');
        });
    }
    
    // Close modals when clicking outside
    window.addEventListener('click', function(e) {
        if (e.target === addItemModal) {
            addItemModal.classList.remove('show');
        }
        
        if (e.target === editItemModal) {
            editItemModal.classList.remove('show');
        }
    });
    
    // Add new item
    if (addItemSubmit && addItemForm) {
        addItemSubmit.addEventListener('click', async function() {
            const nameInput = document.getElementById('item-name');
            const descriptionInput = document.getElementById('item-description');
            const categoryInput = document.getElementById('item-category');
            const statusInput = document.getElementById('item-status');
            const assignedInput = document.getElementById('item-assigned');
            
            if (!nameInput.value.trim()) {
                alert('Please enter an item name');
                return;
            }
            
            if (!currentChecklistId) {
                alert('No checklist available to add items');
                return;
            }
            
            try {
                console.log("Creating new checklist item...");
                
                // Create new item via API
                const apiData = {
                    title: nameInput.value.trim(),
                    status: statusInput.value,
                    checklist_id: currentChecklistId
                };
                
                console.log("Sending data to API:", apiData);
                
                // Use the ChecklistItem API from api-service.js
                const result = await API.ChecklistItem.create(apiData);
                
                console.log("API response:", result);
                
                if (!result || !result.item) {
                    throw new Error("Invalid response from server");
                }
                
                // Add new item with server-generated ID to our local array
            const newItem = {
                    id: result.item.id.toString(),
                    name: result.item.title,
                description: descriptionInput.value.trim(),
                category: categoryInput.value,
                    status: result.item.status,
                    assignedTo: assignedInput.value || null,
                    checklist_id: currentChecklistId
                };
                
                console.log("Created new item:", newItem);
            
                // Add to items array - using our updateItems helper
                const updatedItems = [...items, newItem];
                updateItems(updatedItems);
            
            // Re-render items
            renderItems();
            
            // Reset form
            addItemForm.reset();
            
            // Close modal
            addItemModal.classList.remove('show');
            } catch (error) {
                console.error('Error creating item:', error);
                alert(`Failed to create item: ${error.message}. Please try again.`);
            }
        });
    }
    
    // Edit item
    if (editItemSubmit) {
        editItemSubmit.addEventListener('click', async function() {
            const itemId = document.getElementById('edit-item-id').value;
            const nameInput = document.getElementById('edit-item-name');
            const descriptionInput = document.getElementById('edit-item-description');
            const categoryInput = document.getElementById('edit-item-category');
            const statusInput = document.getElementById('edit-item-status');
            const assignedInput = document.getElementById('edit-item-assigned');
            
            if (!nameInput.value.trim()) {
                alert('Please enter an item name');
                return;
            }
            
            try {
                // Prepare data for API call
                const apiData = {
                    title: nameInput.value.trim(),
                    status: statusInput.value
                };
                
                // Use the ChecklistItem API from api-service.js
                await API.ChecklistItem.update(itemId, apiData);
            
            // Find item index
            const itemIndex = items.findIndex(item => item.id === itemId);
            
            if (itemIndex !== -1) {
                    // Update item locally
                const updatedItems = [...items]; // Create a copy
                updatedItems[itemIndex] = {
                    ...updatedItems[itemIndex],
                    name: nameInput.value.trim(),
                    description: descriptionInput.value.trim(),
                    category: categoryInput.value,
                    status: statusInput.value,
                    assignedTo: assignedInput.value || null
                };
                
                // Update items with helper
                updateItems(updatedItems);
                
                // Re-render items
                renderItems();
                
                // Close modal
                editItemModal.classList.remove('show');
                }
            } catch (error) {
                console.error('Error updating item:', error);
                alert('Failed to update item. Please try again.');
            }
        });
    }
    
    // Function to handle drag start
    function handleDragStart(e) {
        e.dataTransfer.setData('text/plain', e.target.dataset.id);
        e.target.classList.add('dragging');
    }
    
    // Function to handle drag end
    function handleDragEnd(e) {
        e.target.classList.remove('dragging');
    }
    
    // Function to handle drag over
    function handleDragOver(e) {
        e.preventDefault();
    }
    
    // Function to handle drop
    async function handleDrop(e) {
        e.preventDefault();
        
        const id = e.dataTransfer.getData('text/plain');
        const container = e.currentTarget;
        const status = container.dataset.status;
        
        // Find item
        const itemIndex = items.findIndex(item => item.id === id);
        
        if (itemIndex !== -1) {
            // Update status
            const newStatus = status;
            const oldStatus = items[itemIndex].status;
            
            // Only update if status changed
            if (newStatus !== oldStatus) {
                try {
                    // Use the ChecklistItem API from api-service.js
                    await API.ChecklistItem.update(id, { status: newStatus });
                    
                    // Update local item
                    items[itemIndex].status = newStatus;
                    
                    // Save to localStorage
                    updateItems([...items]); // Create a new array to force update
                    
                    // Re-render items
                    renderItems();
                } catch (error) {
                    console.error('Error updating item status:', error);
                    alert('Failed to update item status. Please try again.');
                }
            }
        }
    }
    
    // Render items function
    function renderItems() {
        console.log(`--- RENDER ITEMS START ---`);
        console.log(`Total items to render: ${items.length}`);
        
        // Safety check: Make sure items is an array 
        if (!Array.isArray(items)) {
            console.error("RENDER: Items is not an array!", items);
            // Create a new empty array
            items = [];
            localStorage.setItem('checklist_items', JSON.stringify(items));
            return; // Exit to prevent further errors
        }
        
        // Debug: Print all item IDs before rendering
        if (items.length > 0) {
            console.log('RENDER: Items to render:', items.map(item => `${item.id}:${item.name}`).join(', '));
        } else {
            console.log('RENDER: No items to render');
        }
        
        // Safety: Make sure all containers exist
        if (!toPackContainer || !packedContainer || !deliveredContainer) {
            console.error("RENDER: One or more containers missing!");
            return;
        }
        
        // Clear containers
        toPackContainer.innerHTML = '';
        packedContainer.innerHTML = '';
        deliveredContainer.innerHTML = '';
        
        // Create three separate item arrays - avoid modifying the main items array
        const toPackItems = [];
        const packedItems = [];
        const deliveredItems = [];
        
        // Sort each item into the right category
        items.forEach(item => {
            if (item.status === 'To Pack') {
                toPackItems.push(item);
            } else if (item.status === 'Packed') {
                packedItems.push(item);
            } else if (item.status === 'Delivered') {
                deliveredItems.push(item);
            } else {
                console.warn(`RENDER: Item ${item.id} has unknown status: ${item.status}`);
                toPackItems.push(item); // Default to To Pack
            }
        });
        
        console.log(`RENDER: Sorted items: ${toPackItems.length} to pack, ${packedItems.length} packed, ${deliveredItems.length} delivered`);
        
        // Render to pack items
        renderItemsToContainer(toPackItems, toPackContainer);
        
        // Render packed items
        renderItemsToContainer(packedItems, packedContainer);
        
        // Render delivered items
        renderItemsToContainer(deliveredItems, deliveredContainer);
        
        // Update item counts
        updateItemCounts(toPackItems.length, packedItems.length, deliveredItems.length);
        
        // Remove old listeners and add new ones to avoid duplicates
        toPackContainer.removeEventListener('dragover', handleDragOver);
        toPackContainer.removeEventListener('drop', handleDrop);
        packedContainer.removeEventListener('dragover', handleDragOver);
        packedContainer.removeEventListener('drop', handleDrop);
        deliveredContainer.removeEventListener('dragover', handleDragOver);
        deliveredContainer.removeEventListener('drop', handleDrop);
        
        // Re-add listeners
        toPackContainer.addEventListener('dragover', handleDragOver);
        toPackContainer.addEventListener('drop', handleDrop);
        packedContainer.addEventListener('dragover', handleDragOver);
        packedContainer.addEventListener('drop', handleDrop);
        deliveredContainer.addEventListener('dragover', handleDragOver);
        deliveredContainer.addEventListener('drop', handleDrop);
        
        console.log(`--- RENDER ITEMS COMPLETE ---`);
    }
    
    // Render items to container
    function renderItemsToContainer(items, container) {
        if (!container) {
            console.error("RENDER: Container is null or undefined");
            return;
        }
        
        if (!Array.isArray(items)) {
            console.error("RENDER: Items is not an array in renderItemsToContainer");
            return;
        }
        
        console.log(`RENDER: Adding ${items.length} items to container`);
        
        // Create a document fragment for better performance
        const fragment = document.createDocumentFragment();
        
        items.forEach(item => {
            if (!item || !item.id) {
                console.error("RENDER: Invalid item:", item);
                return; // Skip this item
            }
            
            console.log(`RENDER: Creating element for item ID: ${item.id}, Name: ${item.name}`);
            
        const itemElement = document.createElement('div');
        itemElement.className = 'checklist-item';
        itemElement.dataset.id = item.id;
            itemElement.draggable = true;
            
            // Add data attributes for debugging
            itemElement.setAttribute('data-item-id', item.id);
            itemElement.setAttribute('data-item-status', item.status);
            
            // Add drag event listeners
            itemElement.addEventListener('dragstart', handleDragStart);
            itemElement.addEventListener('dragend', handleDragEnd);
            
            // Create HTML structure
        itemElement.innerHTML = `
                <div class="item-header">
                    <h3>${item.name || 'Unnamed Item'}</h3>
                    <div class="item-actions">
                        <button class="edit-btn" data-id="${item.id}">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="delete-btn" data-id="${item.id}">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
                <div class="item-details">
                    <p>${item.description || 'No description'}</p>
                    <div class="item-meta">
                        <span class="item-category">${item.category || 'General'}</span>
                        ${item.assignedTo ? `<span class="item-assigned">Assigned to: ${item.assignedTo}</span>` : ''}
                </div>
            </div>
        `;
            
            // Add to fragment
            fragment.appendChild(itemElement);
        });
        
        // Add fragment to container all at once (more efficient)
        container.appendChild(fragment);
        
        // Now add event listeners to all buttons
        items.forEach(item => {
            if (!item || !item.id) return; // Skip invalid items
            
            // Find the element we just added
            const itemElement = container.querySelector(`.checklist-item[data-item-id="${item.id}"]`);
            if (!itemElement) {
                console.error(`RENDER: Could not find element for item ${item.id}`);
                return;
            }
            
            // Add edit event listener
            const editBtn = itemElement.querySelector('.edit-btn');
            if (editBtn) {
                editBtn.addEventListener('click', function() {
                    showEditModal(item);
                });
            }
            
            // Add delete event listener
            const deleteBtn = itemElement.querySelector('.delete-btn');
            if (deleteBtn) {
                deleteBtn.addEventListener('click', async function(e) {
                e.preventDefault();
                    e.stopPropagation();
                    
                    const itemId = item.id;
                    console.log(`DELETE: Button clicked for item ${itemId}`);
                    
                    if (confirm('Are you sure you want to delete this item?')) {
                        try {
                            // Call API to delete on server
                            await API.ChecklistItem.delete(itemId);
                            
                            // Create new array without deleted item
                            const newItems = items.filter(i => i.id !== itemId);
                            
                            // Update items with our helper
                            updateItems(newItems);
                            
                            // Re-render everything
                            renderItems();
                            
                            console.log(`Item ${itemId} deleted successfully`);
                        } catch (error) {
                            console.error('Error deleting item:', error);
                            alert('Failed to delete item. Please try again.');
                        }
                    }
                });
            }
        });
    }
    
    // Update item counts
    function updateItemCounts(toPack, packed, delivered) {
        const toPackCount = document.getElementById('to-pack-count');
        const packedCount = document.getElementById('packed-count');
        const deliveredCount = document.getElementById('delivered-count');
        const totalCount = document.getElementById('total-count');
        
        if (toPackCount) toPackCount.textContent = toPack;
        if (packedCount) packedCount.textContent = packed;
        if (deliveredCount) deliveredCount.textContent = delivered;
        if (totalCount) totalCount.textContent = toPack + packed + delivered;
    }
    
    // Show edit modal function
    function showEditModal(item) {
        // Set form values
        document.getElementById('edit-item-id').value = item.id;
        document.getElementById('edit-item-name').value = item.name;
        document.getElementById('edit-item-description').value = item.description || '';
        document.getElementById('edit-item-category').value = item.category;
        document.getElementById('edit-item-status').value = item.status;
        document.getElementById('edit-item-assigned').value = item.assignedTo || '';
        
        // Show modal
        editItemModal.classList.add('show');
    }
});