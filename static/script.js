let serverIP = localStorage.getItem('serverIP') || 'do-i-share-a-class-with-anyone-7a9e11f397f2.herokuapp.com';

// Initialize the input with stored value when page loads
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('serverIP').value = serverIP;
});

function updateServer() {
    const newServerIP = document.getElementById('serverIP').value.trim();
    if (!newServerIP) {
        alert('Please enter a valid server IP');
        return;
    }
    serverIP = newServerIP;
    localStorage.setItem('serverIP', serverIP);
    alert('Server IP updated successfully!');
}

function addClassInput(container) {
    const div = document.createElement('div');
    div.className = 'class-input-group';
    
    const input = document.createElement('input');
    input.type = 'text';
    input.className = 'class-input';
    input.placeholder = 'Class Code (e.g., 11SE1)';
    
    const removeBtn = document.createElement('button');
    removeBtn.textContent = 'X';
    removeBtn.className = 'remove-class';
    removeBtn.onclick = () => div.remove();
    
    div.appendChild(input);
    div.appendChild(removeBtn);
    container.appendChild(div);
}

function validateClassCode(code) {
    if (!code) return false;
    code = code.toUpperCase();
    if (code.length < 4) return false;
    if (!code.slice(0,2).match(/^(7|8|9|10|11|12)$/)) return false;
    return /[A-Z]/.test(code.slice(2));
}

async function submitClasses() {
    const name = document.getElementById('fullName').value;
    const studentId = document.getElementById('studentId').value;
    const classInputs = document.querySelectorAll('.add-classes .class-input');
    const classes = Array.from(classInputs).map(input => input.value.toUpperCase().trim());
    
    // Validation
    if (!name || name.split(' ').length < 2) {
        alert('Please enter your full name (first and last name)');
        return;
    }
    if (!studentId || !studentId.match(/^\d{4,}$/)) {
        alert('Please enter a valid student ID (at least 4 digits)');
        return;
    }
    if (classes.length === 0) {
        alert('Please add at least one class');
        return;
    }
    if (!classes.every(validateClassCode)) {
        alert('Invalid class code format. Example: 11SE1');
        return;
    }

    try {
        const formatted_name = name.replace(/\s+/g, '_');
        const response = await fetch(`https://${serverIP}/add/${formatted_name}/${studentId}/${classes.join(',')}`);
        if (response.ok) {
            alert('Classes added successfully!');
            // Clear the form
            document.getElementById('fullName').value = '';
            document.getElementById('studentId').value = '';
            document.querySelector('.add-classes').innerHTML = '';
        } else {
            alert('Failed to add classes');
        }
    } catch (e) {
        alert(`Error: ${e.message}`);
    }
}

async function searchStudent() {
    const identifier = document.getElementById('searchIdentifier').value.trim();
    const searchResults = document.getElementById('searchResults');
    
    if (!identifier) {
        // Enable manual class entry if no identifier
        document.querySelector('.manual-class-entry').style.display = 'block';
        return;
    }

    try {
        let response;
        if (identifier.match(/^\d{4,}$/)) {
            response = await fetch(`https://${serverIP}/get/student/${identifier}`);
        } else if (identifier.split(' ').length >= 2) {
            const formatted_name = identifier.replace(/\s+/g, '_');
            response = await fetch(`https://${serverIP}/get/student/name/${formatted_name}`);
        }

        if (response.ok) {
            const data = await response.json();
            const classes = data.classes.split(',');
            searchResults.innerHTML = `<p>Found classes: ${classes.join(', ')}</p>`;
            // Add these classes to the search
            const searchClassesDiv = document.querySelector('.search-classes');
            searchClassesDiv.innerHTML = '';
            classes.forEach(classCode => {
                const div = document.createElement('div');
                div.className = 'class-input-group';
                div.innerHTML = `
                    <input type="text" class="class-input" value="${classCode}" readonly>
                `;
                searchClassesDiv.appendChild(div);
            });
        } else {
            searchResults.innerHTML = '<p>No existing classes found. You can enter them manually.</p>';
            document.querySelector('.manual-class-entry').style.display = 'block';
        }
    } catch (e) {
        alert(`Error: ${e.message}`);
    }
}

async function searchLinks() {
    const classInputs = document.querySelectorAll('.search-classes .class-input');
    const classes = Array.from(classInputs).map(input => input.value.toUpperCase().trim());
    
    if (classes.length === 0) {
        alert('Please add at least one class');
        return;
    }

    try {
        const response = await fetch(`https://${serverIP}/get/${classes.join(',')}`);
        const data = await response.json();
        
        const results = document.getElementById('matchResults');
        if (data.match) {
            results.innerHTML = `
                <div class="match-result">
                    <h3>Match Found!</h3>
                    <p>Name: ${data.match.name.replace('_', ' ')}</p>
                    <p>Matching Classes: ${data.match.matching_classes.join(', ')}</p>
                    <p>Their Classes: ${data.match.classes.join(', ')}</p>
                </div>
            `;
        } else {
            results.innerHTML = '<p>No matching students found.</p>';
        }
    } catch (e) {
        alert(`Error: ${e.message}`);
    }
}