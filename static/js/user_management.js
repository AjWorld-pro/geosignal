document.addEventListener('DOMContentLoaded', async () => {
    Spinner.show();
    try {
        await loadUsers();
        setupUserManagementListeners();
    } catch (e) { console.error('User mgmt error:', e); }
    finally { Spinner.hide(); }
});

function getAvatarColor(username) {
    const colors = ['', 'amber', 'emerald', 'purple'];
    let hash = 0;
    for (let i = 0; i < username.length; i++) hash = username.charCodeAt(i) + ((hash << 5) - hash);
    return colors[Math.abs(hash) % colors.length];
}

function getInitials(username) {
    return username.charAt(0).toUpperCase();
}

async function loadUsers() {
    const list = DOM.byId('usersList'); DOM.clear(list);
    try {
        const r = await fetch('/api/core/users/');
        if (!r.ok) throw new Error('Not authorized');
        const users = await r.json();
        const results = users.results || users;
        if (!results.length) {
            list.innerHTML = '<div class="empty-state"><i class="fas fa-users"></i><h3>No users found</h3></div>';
            DOM.byId('userCount').textContent = '0';
            return;
        }
        DOM.byId('userCount').textContent = results.length;
        results.forEach(u => {
            const card = DOM.create('div'); card.className = 'user-card';
            const statusClass = u.is_active ? 'active' : 'suspended';
            card.innerHTML = `
                <div class="user-avatar ${getAvatarColor(u.username)}">${getInitials(u.username)}</div>
                <div class="user-info">
                    <p class="user-name">${u.username}</p>
                    <p class="user-email">${u.email || 'No email'}</p>
                </div>
                <div class="user-meta">
                    <span class="user-status ${statusClass}">${u.is_active ? 'Active' : 'Suspended'}</span>
                </div>
                <div class="user-actions">
                    <button class="btn-action btn-action-edit edit-user" data-id="${u.id}"><i class="fas fa-edit"></i> Edit</button>
                    <button class="btn-action btn-action-delete delete-user" data-id="${u.id}"><i class="fas fa-trash"></i> Delete</button>
                </div>
            `;
            DOM.append(list, card);
        });
    } catch (e) {
        list.innerHTML = '<div class="empty-state"><i class="fas fa-lock"></i><h3>Login as admin to manage users</h3></div>';
        DOM.byId('userCount').textContent = '0';
    }
}

function setupUserManagementListeners() {
    DOM.byId('addUserBtn')?.addEventListener('click', () => { Toast.info('Use Django admin panel to add users'); });
}
