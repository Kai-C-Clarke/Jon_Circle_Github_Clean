// static/js/profile.js - Profile functions

// Load existing profile data
async function loadProfile() {
    try {
        const response = await fetch('/api/profile/get');
        const data = await response.json();
        
        if (data.status === 'success' && data.profile) {
            const profile = data.profile;
            
            // Populate form fields
            if (profile.name) {
                document.getElementById('user-name').value = profile.name;
            }
            if (profile.birth_date) {
                document.getElementById('birth-date').value = profile.birth_date;
            }
            if (profile.birth_place) {
                document.getElementById('birth-place').value = profile.birth_place;
            }
            if (profile.family_role) {
                // Populate roles-tags field with existing data
                document.getElementById('roles-tags').value = profile.family_role;
            }
        }
    } catch (error) {
        console.error('Error loading profile:', error);
    }
}

async function saveProfile() {
    const name = document.getElementById('user-name').value.trim();
    const birthDate = document.getElementById('birth-date').value;
    const rolesInput = document.getElementById('roles-tags').value.trim();
    
    if (!name || !birthDate || !rolesInput) {
        alert('Please fill in all required fields.');
        return;
    }
    
    // Parse tags from comma-separated input
    const roles = rolesInput.split(',').map(tag => tag.trim()).filter(tag => tag.length > 0);
    const familyRole = roles.join(', ');
    
    try {
        const response = await fetch('/api/profile/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: name,
                birth_date: birthDate,
                family_role: familyRole,
                birth_place: document.getElementById('birth-place').value
            })
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            // Update UI
            document.querySelector('h1').textContent = `The Circle: ${name}'s Story`;
            showMainInterface();
            alert(`Welcome to The Circle, ${name}!`);
        }
    } catch (error) {
        console.error('Error saving profile:', error);
        alert('Failed to save profile.');
    }
}

// Call loadProfile on page load if profile exists
document.addEventListener('DOMContentLoaded', loadProfile);