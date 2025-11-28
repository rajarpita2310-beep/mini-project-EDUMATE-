document.addEventListener('DOMContentLoaded', () => {

    // --- CONFIGURATION ---
    const API_BASE_URL = 'http://127.0.0.1:5000/api';
    const EMAILJS_SERVICE_ID = 'service_78oq0lg';
    const EMAILJS_TEMPLATE_ID = 'template_n3dg02m';
    const EMAILJS_PUBLIC_KEY = 'e_fxlsNE_04OYiefP';

    // --- GLOBAL STATE ---
    let currentUser = null;
    let classesData = [];
    let timetableData = [];
    let notificationsData = [];
    let examsData = [];
    let assignmentsData = [];

    const dayOrder = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
    let currentView = 'Dashboard';
    // Restore where the user was (Deep Linking)
    let savedContext = JSON.parse(localStorage.getItem('edumate_context')) || {};
    let currentTimetableView = 'list';
    let selectedExamId = null;

    // --- HELPERS ---
    function setContext(page, subPage=null, id=null, subId=null) {
        currentView = page;
        savedContext = { page, subPage, id, subId };
        localStorage.setItem('edumate_context', JSON.stringify(savedContext));
        document.querySelectorAll('.sidebar-link').forEach(l => l.classList.toggle('active', l.dataset.page === page));
    }
    function checkSession() {
        const u = localStorage.getItem('edumate_user');
        if(u){ currentUser=JSON.parse(u); showAppScreen(); }
    }
    function saveSession(u) { localStorage.setItem('edumate_user', JSON.stringify(u)); }

    // --- FETCHERS ---
    async function fetchClasses() { try{const r=await fetch(`${API_BASE_URL}/classes`); if(r.ok) classesData=await r.json();}catch(e){} }
    async function fetchTimetable() { try{const r=await fetch(`${API_BASE_URL}/timetable`); if(r.ok) timetableData=await r.json();}catch(e){} }
    async function fetchNotifications() { try{const r=await fetch(`${API_BASE_URL}/notifications`); if(r.ok) notificationsData=await r.json();}catch(e){} }
    async function fetchExams() { try{const r=await fetch(`${API_BASE_URL}/exams`); if(r.ok) examsData=await r.json();}catch(e){} }
    async function fetchAssignments() { try{const r=await fetch(`${API_BASE_URL}/assignments`); if(r.ok) assignmentsData=await r.json();}catch(e){} }

    // --- AUTHENTICATION (FIXED) ---
    const loginForm = document.getElementById('login-form');

    document.getElementById('toggle-auth')?.addEventListener('click', (e) => {
        e.preventDefault();
        const btn = document.querySelector('#login-form button');
        const nf = document.getElementById('name-field-container');
        const title = document.querySelector('#login-screen h1');
        const currentText = btn.textContent.trim();

        if (currentText === 'Login') {
            nf.classList.remove('hidden');
            btn.textContent = 'Sign Up';
            e.target.textContent = 'Login instead';
            title.textContent = 'Create Account';
        } else {
            nf.classList.add('hidden');
            btn.textContent = 'Login';
            e.target.textContent = 'Sign Up';
            title.textContent = 'EduMate';
        }
    });

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const btn = document.querySelector('#login-form button');
        const isSignup = btn.textContent.trim() === 'Sign Up';

        const payload = {
            email: document.getElementById('email').value.trim(),
            password: document.getElementById('password').value.trim(),
            name: isSignup ? document.getElementById('name').value.trim() : undefined
        };

        console.log(`Attempting to ${isSignup ? 'Sign Up' : 'Login'}...`, payload);

        try {
            const res = await fetch(`${API_BASE_URL}${isSignup?'/signup':'/login'}`, {
                method: 'POST',
                headers: {'Content-Type':'application/json'},
                body: JSON.stringify(payload)
            });
            const data = await res.json();

            if (res.ok) {
                currentUser = data;
                saveSession(currentUser);
                setContext('Dashboard'); // Reset context on new login
                showAppScreen();
            } else {
                // Use a custom alert box or a visible message instead of built-in alert
                console.error("Authentication Error: " + data.error);
                alert("Error: " + (data.error || "Authentication failed."));
            }
        } catch (err) {
            console.error(err);
            alert("Connection failed! Is the python server running?");
        }
    });

    async function showAppScreen() {
        document.getElementById('login-screen').classList.add('hidden');
        document.getElementById('app-screen').classList.remove('hidden');

        // Load ALL data
        await Promise.all([fetchClasses(), fetchTimetable(), fetchNotifications(), fetchExams(), fetchAssignments()]);

        renderAppShell();

        // Restore Deep State
        if (savedContext.page) {
            if (savedContext.page === 'Class Lists' && savedContext.subPage === 'student_list') renderStudentListView(savedContext.id);
            else if (savedContext.page === 'Class Lists' && savedContext.subPage === 'profile') renderStudentProfile(savedContext.id, savedContext.subId);
            else renderPage(savedContext.page);
        } else renderPage('Dashboard');

        try { emailjs.init(EMAILJS_PUBLIC_KEY); } catch (e) {}
    }

    // --- LAYOUT ---
    function renderAppShell() {
        // Updated header to include avatar using currentUser.profilePic
        document.getElementById('app-screen').innerHTML = `<div class="flex h-screen bg-gray-100"><aside id="sidebar" class="w-64 bg-gray-800 text-white flex flex-col flex-shrink-0"></aside><div class="flex-1 flex flex-col overflow-hidden"><header class="bg-white shadow-md px-6 h-16 flex items-center justify-between"><h1 id="page-title" class="text-xl font-semibold text-gray-800">EduMate</h1><div class="flex items-center gap-3"><img id="header-avatar" src="${currentUser.profilePic}" alt="Avatar" class="w-10 h-10 rounded-full object-cover border-2 border-indigo-300"/><span class="font-medium text-gray-700">Welcome, ${currentUser.name}!</span></div></header><main id="main-content" class="flex-1 overflow-x-hidden overflow-y-auto bg-gray-100 p-6"></main></div></div><div id="modal-container"></div>`;
        // Added 'My Profile' link to the sidebar
        const links = [ { name: 'Dashboard', icon: 'layout-dashboard' }, { name: 'Class Lists', icon: 'users' }, { name: 'Attendance', icon: 'check-circle' }, { name: 'Scores', icon: 'graduation-cap' }, { name: 'Assignments', icon: 'notebook-pen' }, { name: 'Timetable', icon: 'calendar' }, { name: 'Notifications', icon: 'bell' }, { name: 'My Profile', icon: 'user' } ];
        document.getElementById('sidebar').innerHTML = `<div class="h-16 flex items-center justify-center text-2xl font-bold border-b border-gray-700">EduMate</div><nav class="flex-1 px-2 py-4 space-y-2">${links.map(l => `<a href="#" class="sidebar-link flex items-center px-4 py-2.5 rounded-lg hover:bg-gray-700" data-page="${l.name}"><i data-lucide="${l.icon}" class="w-5 h-5 mr-3"></i> ${l.name}</a>`).join('')}</nav><div class="p-4 border-t border-gray-700"><button id="logout-btn" class="w-full flex items-center px-4 py-2 hover:bg-red-600 rounded">Logout</button></div>`;
        document.getElementById('sidebar').addEventListener('click', (e) => { const l = e.target.closest('.sidebar-link'); if(l) renderPage(l.dataset.page); });
        document.getElementById('logout-btn').addEventListener('click', () => { localStorage.clear(); window.location.reload(); });
    }

    async function renderPage(pageName) {
        setContext(pageName);
        document.getElementById('page-title').textContent = pageName;
        const content = document.getElementById('main-content');
        if (pageName === 'Dashboard') renderDashboard(content);
        else if (pageName === 'Class Lists') { await fetchClasses(); renderClassLists(content); }
        else if (pageName === 'Timetable') { await fetchTimetable(); renderTimetableContainer(content); }
        else if (pageName === 'Notifications') { await fetchNotifications(); renderNotifications(content); }
        else if (pageName === 'Attendance') { await fetchClasses(); await fetchTimetable(); renderAttendancePage(content); }
        else if (pageName === 'Scores') { await fetchExams(); await fetchClasses(); renderScoresPage(content); }
        else if (pageName === 'Assignments') { await fetchAssignments(); renderAssignmentsPage(content); }
        else if (pageName === 'My Profile') { renderTeacherProfile(content); }
        lucide.createIcons();
    }

    // --- NEW: TEACHER PROFILE ---
    function renderTeacherProfile(c) {
        const profile = currentUser;
        c.innerHTML = `
            <div class="max-w-xl mx-auto bg-white p-8 rounded-xl shadow-lg">
                <h2 class="text-3xl font-bold mb-6 text-indigo-700">My Profile</h2>
                <div class="flex flex-col items-center mb-6">
                    <img id="profile-avatar" src="${profile.profilePic}" alt="Profile Photo" class="w-32 h-32 rounded-full object-cover mb-4 border-4 border-indigo-200 shadow-md">
                    <h3 class="text-xl font-semibold">${profile.name}</h3>
                    <p class="text-gray-500">${profile.email}</p>

                    <div class="mt-4 text-sm text-gray-700 space-y-1 text-center">
                        ${profile.subject ? `<p class="flex items-center gap-2"><i data-lucide="book-open" class="w-4 h-4 text-indigo-500"></i> Teaches: ${profile.subject}</p>` : ''}
                        ${profile.phone ? `<p class="flex items-center gap-2"><i data-lucide="phone" class="w-4 h-4 text-green-500"></i> Phone: <a href="tel:${profile.phone}">${profile.phone}</a></p>` : ''}
                        ${profile.gender ? `<p class="flex items-center gap-2"><i data-lucide="user" class="w-4 h-4 text-gray-500"></i> Gender: ${profile.gender}</p>` : ''}
                        ${profile.birthday ? `<p class="flex items-center gap-2"><i data-lucide="cake" class="w-4 h-4 text-pink-500"></i> Birthday: ${new Date(profile.birthday).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}</p>` : ''}
                        ${profile.address ? `<p class="flex items-center gap-2 text-center"><i data-lucide="map-pin" class="w-4 h-4 text-red-500"></i> Address: ${profile.address}</p>` : ''}
                    </div>
                    </div>
                <form id="teacher-profile-form" class="space-y-4">
                    <div class="grid grid-cols-2 gap-4">
                        <div>
                            <label for="p-name" class="block text-sm font-medium text-gray-700">Full Name</label>
                            <input type="text" id="p-name" value="${profile.name}" class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-3 focus:ring-indigo-500 focus:border-indigo-500">
                        </div>

                        <div>
                            <label for="p-email" class="block text-sm font-medium text-gray-700">Email (Read Only)</label>
                            <input type="email" id="p-email" value="${profile.email}" disabled class="mt-1 block w-full border border-gray-200 bg-gray-50 rounded-md shadow-sm p-3">
                        </div>

                        <div>
                            <label for="p-phone" class="block text-sm font-medium text-gray-700">Phone Number</label>
                            <input type="tel" id="p-phone" value="${profile.phone || ''}" class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-3 focus:ring-indigo-500 focus:border-indigo-500">
                        </div>

                        <div>
                            <label for="p-gender" class="block text-sm font-medium text-gray-700">Gender</label>
                            <select id="p-gender" class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-3 focus:ring-indigo-500 focus:border-indigo-500">
                                <option value="">Select</option>
                                <option value="Male" ${profile.gender === 'Male' ? 'selected' : ''}>Male</option>
                                <option value="Female" ${profile.gender === 'Female' ? 'selected' : ''}>Female</option>
                                <option value="Other" ${profile.gender === 'Other' ? 'selected' : ''}>Other</option>
                            </select>
                        </div>

                        <div>
                            <label for="p-bday" class="block text-sm font-medium text-gray-700">Birthday</label>
                            <input type="date" id="p-bday" value="${profile.birthday || ''}" class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-3 focus:ring-indigo-500 focus:border-indigo-500">
                        </div>

                        <div>
                            <label for="p-subject" class="block text-sm font-medium text-gray-700">Subject(s) Taught</label>
                            <input type="text" id="p-subject" value="${profile.subject || ''}" class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-3 focus:ring-indigo-500 focus:border-indigo-500" placeholder="Math, Science, History, etc.">
                        </div>
                    </div>

                    <div>
                        <label for="p-address" class="block text-sm font-medium text-gray-700">Address</label>
                        <textarea id="p-address" rows="2" class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-3 focus:ring-indigo-500 focus:border-indigo-500">${profile.address || ''}</textarea>
                    </div>

                    <div>
                        <label for="p-pic" class="block text-sm font-medium text-gray-700">Profile Picture URL</label>
                        <input type="url" id="p-pic" value="${profile.profilePic}" class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-3 focus:ring-indigo-500 focus:border-indigo-500" onchange="document.getElementById('profile-avatar').src = this.value || 'https://placehold.co/100x100/A5B4FC/3730A3?text=TP'">
                    </div>

                    <div class="pt-4">
                        <button type="submit" class="w-full bg-indigo-600 text-white font-semibold py-3 rounded-lg hover:bg-indigo-700 transition-transform transform hover:scale-[1.01]">
                            Save Changes
                        </button>
                    </div>
                </form>
            </div>
        `;
        lucide.createIcons();

        document.getElementById('teacher-profile-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const newName = document.getElementById('p-name').value.trim();
            const newPic = document.getElementById('p-pic').value.trim();
            const newPhone = document.getElementById('p-phone').value.trim();
            const newGender = document.getElementById('p-gender').value;
            const newBday = document.getElementById('p-bday').value;
            const newSubject = document.getElementById('p-subject').value.trim();
            const newAddress = document.getElementById('p-address').value.trim();


            if (!newName) return alert('Name cannot be empty.');

            try {
                const res = await fetch(`${API_BASE_URL}/teacher/${currentUser.id}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        name: newName,
                        profilePic: newPic,
                        phone: newPhone,
                        gender: newGender,
                        birthday: newBday,
                        subject: newSubject,
                        address: newAddress
                    })
                });
                const data = await res.json();

                if (res.ok) {
                    currentUser = data; // Update global state
                    saveSession(currentUser); // Update localStorage
                    alert('Profile updated successfully!');
                    renderPage('My Profile'); // Re-render the page to show new details
                    // Also update the header avatar instantly
                    document.getElementById('header-avatar').src = currentUser.profilePic;
                } else {
                    alert('Failed to update profile: ' + (data.error || 'Unknown error'));
                }
            } catch (error) {
                console.error('Update failed:', error);
                alert('An error occurred during update.');
            }
        });
    }

    // --- DASHBOARD ---
    function renderDashboard(c) {
        c.innerHTML = `<div class="grid grid-cols-1 lg:grid-cols-2 gap-6"><div class="bg-white p-6 rounded-xl shadow"><h2 class="text-2xl font-bold mb-2">Welcome back!</h2><p class="text-gray-600 mb-4">Manage your classroom efficiently.</p><div class="flex gap-4"><div class="bg-indigo-50 p-4 rounded-lg text-center flex-1"><h3 class="text-2xl font-bold text-indigo-600">${classesData.length}</h3><p class="text-sm text-gray-500">Classes</p></div><div class="bg-green-50 p-4 rounded-lg text-center flex-1"><h3 class="text-2xl font-bold text-green-600">${examsData.length}</h3><p class="text-sm text-gray-500">Exams Created</p></div></div></div><div class="bg-yellow-50 p-6 rounded-xl shadow border border-yellow-200 relative"><div class="flex justify-between items-center mb-2"><h3 class="font-bold text-yellow-800 flex items-center gap-2"><i data-lucide="sticky-note"></i> Notepad</h3><span id="note-status" class="text-xs text-gray-500"></span></div><textarea id="dash-notepad" class="w-full h-40 bg-transparent border-none resize-none focus:ring-0 text-gray-700" placeholder="Type notes here...">${currentUser.notepad || ''}</textarea></div></div>`;
        const ta = document.getElementById('dash-notepad'); let to;
        ta.addEventListener('input', () => {
            clearTimeout(to); to = setTimeout(async () => {
                await fetch(`${API_BASE_URL}/teacher/${currentUser.id}/notepad`, { method: 'PUT', headers: {'Content-Type':'application/json'}, body: JSON.stringify({ notepad: ta.value }) });
                currentUser.notepad = ta.value; localStorage.setItem('edumate_user', JSON.stringify(currentUser)); document.getElementById('note-status').textContent = 'Saved'; setTimeout(()=>document.getElementById('note-status').textContent='',2000);
            }, 1000);
        });
        lucide.createIcons();
    }

    // --- CLASS LISTS ---
    function renderClassLists(c) {
        setContext('Class Lists');
        const h = classesData.map(x => `<div class="bg-white p-6 rounded-xl shadow-lg mb-4"><div class="flex justify-between"><div><h3 class="text-xl font-bold text-indigo-700">${x.name}</h3><p class="text-gray-600">Coord: ${x.coordinatorName}</p></div><div class="flex gap-2"><button class="view-students px-3 py-1 bg-indigo-100 text-indigo-700 rounded" data-id="${x.id}">View</button><button class="del-class text-red-500" data-id="${x.id}"><i data-lucide="trash-2"></i></button></div></div><div class="mt-4 pt-4 border-t"><span class="text-sm">${x.students.length} Students</span></div></div>`).join('');
        c.innerHTML = `<div class="flex justify-between mb-6"><h2 class="text-2xl font-bold">Classes</h2><button id="add-cls-btn" class="bg-green-600 text-white px-4 py-2 rounded flex gap-2"><i data-lucide="plus"></i> Add Class</button></div><div class="grid gap-4 grid-cols-1 md:grid-cols-2">${h || '<p>No classes.</p>'}</div>`;
        c.querySelector('#add-cls-btn').addEventListener('click', openAddClassModal);
        c.querySelectorAll('.del-class').forEach(b => b.addEventListener('click', async () => { if(confirm('Delete?')) { await fetch(`${API_BASE_URL}/classes/${b.dataset.id}`, {method:'DELETE'}); await fetchClasses(); renderClassLists(c); } }));
        c.querySelectorAll('.view-students').forEach(b => b.addEventListener('click', () => renderStudentListView(b.dataset.id)));
        lucide.createIcons();
    }

    function renderStudentListView(id) {
        setContext('Class Lists', 'student_list', id);
        const cl = classesData.find(c => c.id === id);
        if (!cl) return renderClassLists(document.getElementById('main-content'));
        const r = cl.students.sort((a, b) => a.roll.localeCompare(b.roll, undefined, { numeric: true })).map(s => `<tr class="border-b"><td class="p-3">${s.roll}</td><td class="p-3 font-medium text-indigo-600 cursor-pointer slink" data-id="${s.id}">${s.name}</td><td class="p-3 text-right"><button class="del-std text-red-500" data-id="${s.id}"><i data-lucide="trash-2"></i></button></td></tr>`).join('');
        const c = document.getElementById('main-content');
        c.innerHTML = `<button id="back-btn" class="mb-4 text-indigo-600 flex items-center gap-1"><i data-lucide="arrow-left"></i> Back</button><div class="bg-white p-6 rounded shadow"><div class="flex justify-between mb-4 items-center"><h2 class="text-xl font-bold">${cl.name}</h2><button id="add-std" class="bg-indigo-600 text-white px-4 py-2 rounded flex gap-2"><i data-lucide="plus"></i> Add Student</button></div><table class="w-full text-left"><thead><tr class="bg-gray-50"><th>Roll</th><th>Name</th><th></th></tr></thead><tbody>${r}</tbody></table></div>`;
        lucide.createIcons();
        document.getElementById('back-btn').addEventListener('click', () => renderClassLists(c));
        document.getElementById('add-std').addEventListener('click', () => openAddStudentModal(id));
        c.querySelectorAll('.del-std').forEach(b => b.addEventListener('click', async () => { if(confirm('Delete?')) { await fetch(`${API_BASE_URL}/students/${b.dataset.id}`, {method:'DELETE'}); await fetchClasses(); renderStudentListView(id); } }));
        c.querySelectorAll('.slink').forEach(b => b.addEventListener('click', (e) => renderStudentProfile(id, e.currentTarget.dataset.id)));
    }

    async function renderStudentProfile(cid, sid) {
        setContext('Class Lists', 'profile', cid, sid);
        const cl = classesData.find(c => c.id === cid);
        const st = cl.students.find(s => s.id === sid);
        const c = document.getElementById('main-content');

        let analytics = { attendance: { percentage: 0, total: 0, present: 0 }, scores: [], notes: '' };
        try { const res = await fetch(`${API_BASE_URL}/students/${sid}/analytics`); if (res.ok) analytics = await res.json(); } catch (e) {}
        const call = (n) => n ? `<a href="tel:${n}" class="bg-green-600 text-white p-2 rounded flex items-center justify-center"><i data-lucide="phone" class="w-4 h-4"></i></a>` : '';

        c.innerHTML = `
            <button id="back-list" class="mb-4 text-indigo-600 flex gap-1"><i data-lucide="arrow-left"></i> Back to List</button>
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div class="lg:col-span-2 space-y-6">
                    <div class="bg-white p-8 rounded shadow">
                        <h2 class="text-3xl font-bold mb-6">${st.name} <span class="text-base font-normal text-gray-500">(${st.roll})</span></h2>
                        <form id="prof-form" class="grid gap-4 grid-cols-2">
                            <div><label class="block text-sm font-bold text-gray-700">Status</label><select id="p-st" class="border p-2 w-full rounded"><option ${st.status==='Day Scholar'?'selected':''}>Day Scholar</option><option ${st.status==='Hosteller'?'selected':''}>Hosteller</option></select></div>
                            <div><label class="block text-sm font-bold text-gray-700">Phone</label><div class="flex gap-2"><input id="p-ph" value="${st.phone}" class="border p-2 w-full rounded">${call(st.phone)}</div></div>
                            <div class="col-span-2"><label class="block text-sm font-bold text-gray-700">Student Email</label><input id="p-em" value="${st.email}" class="border p-2 w-full rounded"></div>
                            <div><label class="block text-sm font-bold text-gray-700">Parent Phone</label><div class="flex gap-2"><input id="p-pph" value="${st.parentPhone}" class="border p-2 w-full rounded">${call(st.parentPhone)}</div></div>
                            <div><label class="block text-sm font-bold text-gray-700">Parent Email</label><input id="p-pem" value="${st.parentEmail}" class="border p-2 w-full rounded"></div>
                            <div class="col-span-2 pt-4 text-right"><button class="bg-indigo-600 text-white px-6 py-2 rounded hover:bg-indigo-700">Save Profile</button></div>
                        </form>
                    </div>
                    <div class="bg-white p-8 rounded shadow">
                        <h3 class="text-xl font-bold mb-4">Teacher Notes</h3>
                        <textarea id="student-note" class="w-full h-40 border p-2 rounded resize-none focus:ring-indigo-500" placeholder="Type private notes about this student here...">${analytics.notes}</textarea>
                        <div class="text-right mt-4"><button id="save-note" class="bg-indigo-600 text-white px-6 py-2 rounded hover:bg-indigo-700">Save Notes</button></div>
                    </div>
                </div>
                <div class="lg:col-span-1 space-y-6">
                    <div class="bg-white p-6 rounded shadow text-center">
                        <h3 class="text-lg font-bold text-gray-700 mb-2">Attendance</h3>
                        <div class="text-4xl font-bold ${analytics.attendance.percentage < 75 ? 'text-red-500' : 'text-green-500'}">${analytics.attendance.percentage}%</div>
                        <p class="text-sm text-gray-500 mt-1">${analytics.attendance.present} / ${analytics.attendance.total} Days Present</p>
                    </div>
                    <div class="bg-white p-6 rounded shadow">
                        <h3 class="text-lg font-bold text-gray-700 mb-4">Performance</h3>
                        <div class="space-y-3 max-h-60 overflow-y-auto">
                            ${analytics.scores.length ? analytics.scores.map(s => `<div class="flex justify-between items-center border-b pb-2"><span class="font-medium text-gray-800">${s.exam}</span><span class="font-bold text-indigo-600">${s.obtained} <span class="text-gray-400 text-xs font-normal">/ ${s.total}</span></span></div>`).join('') : '<p class="text-gray-400 italic text-sm">No exams taken yet.</p>'}
                        </div>
                    </div>
                </div>
            </div>`;
        lucide.createIcons();
        document.getElementById('back-list').addEventListener('click', () => renderStudentListView(cid));
        document.getElementById('prof-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            await fetch(`${API_BASE_URL}/students/${sid}`, { method: 'PUT', headers: {'Content-Type':'application/json'}, body: JSON.stringify({ status: document.getElementById('p-st').value, phone: document.getElementById('p-ph').value, email: document.getElementById('p-em').value, parentPhone: document.getElementById('p-pph').value, parentEmail: document.getElementById('p-pem').value }) });
            await fetchClasses(); renderStudentProfile(cid, sid); alert('Profile Saved!');
        });
        document.getElementById('save-note').addEventListener('click', async () => {
            const content = document.getElementById('student-note').value;
            await fetch(`${API_BASE_URL}/students/${sid}/notes`, {
                method: 'PUT',
                headers: {'Content-Type':'application/json'},
                body: JSON.stringify({ content: content })
            });
            alert('Notes Saved!');
            await fetchClasses();
            renderStudentProfile(cid, sid);
        });
    }

    // --- ASSIGNMENTS (UPDATED) ---
    function renderAssignmentsPage(c) {
        // Sort assignments by due date
        const sortedAssignments = assignmentsData.slice().sort((a, b) => new Date(a.dueDate) - new Date(b.dueDate));

        const listHtml = sortedAssignments.map(a => {
            const isOverdue = new Date(a.dueDate) < new Date();
            const dueDateDisplay = new Date(a.dueDate).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
            return `<div class="bg-white p-5 rounded-xl shadow mb-4 ${isOverdue ? 'border-l-4 border-red-500' : 'border-l-4 border-indigo-500'}">
                <div class="flex justify-between items-start">
                    <div>
                        <h3 class="text-xl font-bold text-gray-800">${a.title}</h3>
                        <p class="text-sm text-gray-600 mb-2">${a.className}</p>
                        <p class="text-sm text-gray-500">Due: <span class="font-semibold ${isOverdue ? 'text-red-500' : 'text-green-600'}">${dueDateDisplay}</span></p>
                        ${a.fileUrl ? `<p class="mt-2"><a href="${a.fileUrl}" target="_blank" class="text-indigo-600 text-sm flex items-center gap-1 hover:underline"><i data-lucide="file-text" class="w-4 h-4"></i> View Attached Document</a></p>` : ''}
                    </div>
                    <div class="flex gap-2">
                        <button class="track-ass px-3 py-1 bg-indigo-100 text-indigo-700 rounded text-sm hover:bg-indigo-200" data-id="${a.id}" data-title="${a.title}" data-class="${a.className}">Track Submissions</button>
                        <button class="del-ass text-red-500" data-id="${a.id}"><i data-lucide="trash-2"></i></button>
                    </div>
                </div>
                <p class="mt-3 text-gray-700 text-sm border-t pt-3">${a.description || 'No description provided.'}</p>
            </div>`;
        }).join('');

        c.innerHTML = `<div class="flex justify-between mb-6">
            <h2 class="text-2xl font-bold">Assignments</h2>
            <button id="add-ass-btn" class="bg-indigo-600 text-white px-4 py-2 rounded flex gap-2"><i data-lucide="plus"></i> Add Assignment</button>
        </div>
        <div>${listHtml || '<p class="text-center text-gray-500 py-10">No assignments scheduled yet.</p>'}</div>`;

        c.querySelector('#add-ass-btn').addEventListener('click', openAddAssignmentModal);
        c.querySelectorAll('.del-ass').forEach(b => b.addEventListener('click', async () => {
            if(confirm('Delete this assignment?')) {
                await fetch(`${API_BASE_URL}/assignments/${b.dataset.id}`, {method:'DELETE'});
                await fetchAssignments();
                renderAssignmentsPage(c);
            }
        }));
        // NEW: Track submissions listener
        c.querySelectorAll('.track-ass').forEach(b => b.addEventListener('click', (e) => openSubmissionModal(e.currentTarget.dataset.id, e.currentTarget.dataset.title, e.currentTarget.dataset.class)));
        
        lucide.createIcons();
    }

    function openAddAssignmentModal() {
        const classOptions = classesData.map(x => `<option value="${x.name}">${x.name}</option>`).join('');

        document.getElementById('modal-container').innerHTML = `<div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"><div class="bg-white p-6 rounded-xl shadow w-full max-w-lg"><h2 class="text-xl font-bold mb-4">Create New Assignment</h2>
            <input id="ass-title" class="border p-2 w-full mb-2" placeholder="Assignment Title (e.g., Chapter 3 Homework)">
            <select id="ass-cls" class="w-full border p-2 mb-2">${classOptions || '<option disabled selected>No Classes Available</option>'}</select>
            <input type="date" id="ass-due" class="border p-2 w-full mb-2">
            <input type="url" id="ass-file-url" class="border p-2 w-full mb-2" placeholder="Link to document/file (e.g., Google Drive link)">
            <textarea id="ass-desc" class="w-full border p-2 mb-4" rows="3" placeholder="Detailed Instructions..."></textarea>
            <div class="flex justify-end gap-2"><button id="c-ass" class="bg-gray-200 px-4 py-2 rounded">Cancel</button><button id="s-ass" class="bg-indigo-600 text-white px-4 py-2 rounded">Save Assignment</button></div>
        </div></div>`;

        document.getElementById('c-ass').addEventListener('click', () => document.getElementById('modal-container').innerHTML = '');
        document.getElementById('s-ass').addEventListener('click', async () => {
            const title = document.getElementById('ass-title').value.trim();
            const className = document.getElementById('ass-cls').value;
            const dueDate = document.getElementById('ass-due').value;
            const description = document.getElementById('ass-desc').value.trim();
            const fileUrl = document.getElementById('ass-file-url').value.trim(); // NEW
            const createdAt = new Date().toLocaleString();

            if (!title || !className || !dueDate) {
                return alert('Please fill in the Title, Class, and Due Date.');
            }

            const res = await fetch(`${API_BASE_URL}/assignments`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    title: title,
                    className: className,
                    dueDate: dueDate,
                    description: description,
                    fileUrl: fileUrl, // NEW
                    createdAt: createdAt
                })
            });

            const data = await res.json();

            if (res.ok) {
                document.getElementById('modal-container').innerHTML = '';
                await fetchAssignments();
                await fetchNotifications();

                // Trigger Email Notification using the message returned from Flask
                sendNotificationEmails(data.className, data.notificationMessage);

                renderAssignmentsPage(document.getElementById('main-content'));
            } else {
                alert("Error saving assignment: " + data.error);
            }
        });
    }

    // NEW: SUBMISSION TRACKING MODAL
    async function openSubmissionModal(assignmentId, title, className) {
        const modalContainer = document.getElementById('modal-container');
        modalContainer.innerHTML = `<div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"><div class="bg-white rounded-xl shadow-lg w-full max-w-4xl max-h-[90vh] flex flex-col modal-content"><div class="p-6 border-b flex justify-between items-center"><h2 class="font-bold text-xl">Submissions: ${title} <span class="text-base text-gray-500">(${className})</span></h2><button id="close-sub-modal" class="text-gray-500 hover:text-gray-800"><i data-lucide="x" class="w-6 h-6"></i></button></div><div class="p-6 overflow-y-auto flex-1"><div id="submission-list">Loading submissions...</div></div><div class="p-4 border-t text-right"><button id="save-grades-btn" class="bg-green-600 text-white px-6 py-2 rounded hover:bg-green-700" disabled>Save Grades</button></div></div></div>`;
        lucide.createIcons();
        document.getElementById('close-sub-modal').addEventListener('click', () => modalContainer.innerHTML = '');
        document.getElementById('save-grades-btn').addEventListener('click', saveGrades);

        const submissions = await fetchSubmissions(assignmentId);
        renderSubmissionList(submissions, assignmentId);
    }

    async function fetchSubmissions(assignmentId) {
        try {
            const res = await fetch(`${API_BASE_URL}/submissions/${assignmentId}`);
            if (res.ok) return await res.json();
            return [];
        } catch (e) {
            console.error('Error fetching submissions:', e);
            return [];
        }
    }

    function renderSubmissionList(submissions, assignmentId) {
        const listEl = document.getElementById('submission-list');
        const saveBtn = document.getElementById('save-grades-btn');

        if (submissions.length === 0) {
            listEl.innerHTML = `<p class="text-center text-gray-500 py-10">No students found for this class.</p>`;
            saveBtn.disabled = true;
            return;
        }
        
        // Sort by status, then roll number
        submissions.sort((a, b) => {
            if (a.status === 'Submitted' && b.status !== 'Submitted') return -1;
            if (a.status !== 'Submitted' && b.status === 'Submitted') return 1;
            return a.studentRoll.localeCompare(b.studentRoll, undefined, { numeric: true });
        });

        const tableRows = submissions.map(sub => {
            let statusColor = 'text-gray-500';
            if (sub.status === 'Submitted') statusColor = 'text-green-600 font-medium';
            else if (sub.status === 'Not Submitted') statusColor = 'text-red-500';
            else if (sub.status === 'Graded') statusColor = 'text-indigo-600';

            return `<tr class="border-b hover:bg-gray-50" data-sub-id="${sub.id}">
                <td class="p-3">${sub.studentRoll}</td>
                <td class="p-3 font-medium">${sub.studentName}</td>
                <td class="p-3"><span class="${statusColor}">${sub.status}</span></td>
                <td class="p-3">${sub.submittedOn || '-'}</td>
                <td class="p-3">
                    <input type="text" class="sub-grade border p-1 rounded w-20 text-center" value="${sub.grade}" placeholder="Grade">
                </td>
                <td class="p-3">
                    <textarea class="sub-feedback border p-1 rounded w-full resize-none" rows="1" placeholder="Feedback">${sub.feedback}</textarea>
                </td>
            </tr>`;
        }).join('');

        listEl.innerHTML = `
            <table class="w-full text-left">
                <thead>
                    <tr class="bg-gray-50 text-sm font-semibold">
                        <th class="p-3">Roll</th>
                        <th class="p-3">Student</th>
                        <th class="p-3">Status</th>
                        <th class="p-3">Submitted On</th>
                        <th class="p-3">Grade</th>
                        <th class="p-3">Feedback</th>
                    </tr>
                </thead>
                <tbody>${tableRows}</tbody>
            </table>
        `;
        saveBtn.disabled = false;
        // Store current submissions data for saving
        listEl.dataset.submissions = JSON.stringify(submissions); 
    }

    async function saveGrades() {
        const listEl = document.getElementById('submission-list');
        const rows = listEl.querySelectorAll('tr[data-sub-id]');
        const updates = [];

        // Parse the initial state from the data attribute
        const originalSubmissions = JSON.parse(listEl.dataset.submissions || '[]');

        rows.forEach(row => {
            const subId = row.dataset.subId;
            const grade = row.querySelector('.sub-grade').value.trim();
            const feedback = row.querySelector('.sub-feedback').value.trim();
            
            const originalSub = originalSubmissions.find(s => s.id === subId);

            if (originalSub && (originalSub.grade !== grade || originalSub.feedback !== feedback)) {
                let newStatus = originalSub.status;
                
                // If a grade is entered (and it's not empty)
                if (grade) {
                    // Automatically update status to 'Graded' if it wasn't 'Not Submitted'
                    if (newStatus !== 'Not Submitted') {
                         newStatus = 'Graded';
                    }
                }

                updates.push({
                    id: subId,
                    grade: grade,
                    feedback: feedback,
                    status: newStatus
                });
            }
        });

        if (updates.length === 0) {
            return alert('No changes detected to save.');
        }
        
        document.getElementById('save-grades-btn').textContent = 'Saving...';
        document.getElementById('save-grades-btn').disabled = true;

        try {
            // Use Promise.all to send all update requests concurrently
            const results = await Promise.all(updates.map(update => fetch(`${API_BASE_URL}/submissions`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(update)
            })));
            
            const successful = results.every(res => res.ok);

            if (successful) {
                 alert('Grades and feedback saved successfully!');
            } else {
                alert('Some updates failed. Check console for details.');
            }

            // Close the modal and re-render the page
            document.getElementById('modal-container').innerHTML = '';

        } catch (error) {
            console.error('Failed to save submissions:', error);
            alert('An error occurred during save.');
        }
    }


    // --- MODALS (Unchanged for Class/Student) ---
    function openAddClassModal() {
        document.getElementById('modal-container').innerHTML = `<div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"><div class="bg-white p-6 rounded w-96"><h2 class="text-xl font-bold mb-4">Add Class</h2><input id="n-cn" class="border p-2 w-full mb-2" placeholder="Name"><input id="n-corn" class="border p-2 w-full mb-2" placeholder="Coord Name"><input id="n-corp" class="border p-2 w-full mb-4" placeholder="Coord Phone"><div class="flex justify-end gap-2"><button id="c-cl" class="bg-gray-200 px-4 py-2 rounded">Cancel</button><button id="s-cl" class="bg-indigo-600 text-white px-4 py-2 rounded">Save</button></div></div></div>`;
        document.getElementById('c-cl').addEventListener('click', () => document.getElementById('modal-container').innerHTML = '');
        document.getElementById('s-cl').addEventListener('click', async () => {
            await fetch(`${API_BASE_URL}/classes`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name: document.getElementById('n-cn').value, coordinatorName: document.getElementById('n-corn').value, coordinatorPhone: document.getElementById('n-corp').value }) });
            document.getElementById('modal-container').innerHTML = ''; await fetchClasses(); renderClassLists(document.getElementById('main-content'));
        });
    }
    function openAddStudentModal(cid) {
        document.getElementById('modal-container').innerHTML = `<div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"><div class="bg-white p-6 rounded w-96"><h2 class="text-xl font-bold mb-4">Add Student</h2><input id="n-sn" class="border p-2 w-full mb-2" placeholder="Name"><input id="n-sr" class="border p-2 w-full mb-4" placeholder="Roll"><div class="flex justify-end gap-2"><button id="c-st" class="bg-gray-200 px-4 py-2 rounded">Cancel</button><button id="s-st" class="bg-indigo-600 text-white px-4 py-2 rounded">Save</button></div></div></div>`;
        document.getElementById('c-st').addEventListener('click', () => document.getElementById('modal-container').innerHTML = '');
        document.getElementById('s-st').addEventListener('click', async () => {
            await fetch(`${API_BASE_URL}/classes/${cid}/students`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name: document.getElementById('n-sn').value, roll: document.getElementById('n-sr').value }) });
            document.getElementById('modal-container').innerHTML = ''; await fetchClasses(); renderStudentListView(cid);
        });
    }

    // --- TIMETABLE ---
    function renderTimetableContainer(c){const l=currentTimetableView==='list';c.innerHTML=`<div class="flex justify-between mb-4"><h2 class="text-2xl font-bold">Timetable</h2><div class="bg-gray-200 p-1 rounded flex"><button id="vl" class="px-3 py-1 rounded text-sm ${l?'bg-white shadow text-indigo-600':'text-gray-600'}">List</button><button id="vt" class="px-3 py-1 rounded text-sm ${!l?'bg-white shadow text-indigo-600':'text-gray-600'}">Table</button></div></div><div id="tt-c"></div>`;document.getElementById('vl').addEventListener('click',()=>{currentTimetableView='list';renderTimetableContainer(c)});document.getElementById('vt').addEventListener('click',()=>{currentTimetableView='table';renderTimetableContainer(c)});const content=document.getElementById('tt-c');if(l)renderTimetableList(content);else renderTimetableTable(content);}
    function renderTimetableList(c){let h='';dayOrder.forEach(d=>{const e=timetableData.filter(t=>t.day===d).sort((a,b)=>a.time.localeCompare(b.time));h+=`<div class="bg-white p-5 rounded-xl shadow mb-4"><h3 class="text-lg font-bold mb-3 border-b pb-2">${d}</h3>${e.map(t=>`<div class="p-3 bg-gray-50 border rounded flex justify-between mb-2"><div><span class="font-bold text-indigo-600 mr-2">${t.time}</span><span>${t.subject}</span></div><button class="del-t text-red-400" data-id="${t.id}"><i data-lucide="x" class="w-4 h-4"></i></button></div>`).join('')}<button class="add-t mt-2 w-full py-2 border border-dashed border-indigo-300 text-indigo-600 rounded text-sm" data-day="${d}">Add Class</button></div>`;});c.innerHTML=h;lucide.createIcons();c.querySelectorAll('.add-t').forEach(b=>b.addEventListener('click',()=>openAddTimeModal(b.dataset.day)));c.querySelectorAll('.del-t').forEach(b=>b.addEventListener('click',async()=>{if(confirm('Delete?')){await fetch(`${API_BASE_URL}/timetable/${b.dataset.id}`,{method:'DELETE'});await fetchTimetable();renderTimetableContainer(document.getElementById('main-content'));}}));}
    function renderTimetableTable(c){const times=[...new Set(timetableData.map(t=>t.time))].sort();let h='<tr><th class="border p-2 bg-gray-100">Time</th>'+dayOrder.map(d=>`<th class="border p-2 bg-gray-100">${d}</th>`).join('')+'</tr>';let b=times.map(tm=>{let r=`<tr><td class="border p-2 font-bold">${tm}</td>`;dayOrder.forEach(d=>{const e=timetableData.find(t=>t.time===tm&&t.day===d);r+=`<td class="border p-2 text-sm ${e?'bg-indigo-50':''}">${e?`<b>${e.subject}</b><br>${e.teacher}`:''}</td>`;});return r+'</tr>';}).join('');c.innerHTML=`<div class="bg-white p-4 rounded shadow overflow-x-auto"><table class="w-full border-collapse text-center">${h}${b}</table></div>`;}
    function openAddTimeModal(d){document.getElementById('modal-container').innerHTML=`<div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"><div class="bg-white p-6 rounded w-96"><h2 class="text-xl font-bold mb-4">Add Class</h2><select id="tt-d" class="border p-2 w-full mb-2">${dayOrder.map(x=>`<option ${x===d?'selected':''}>${x}</option>`).join('')}</select><input type="time" id="tt-tm" class="border p-2 w-full mb-2"><input id="tt-sub" class="border p-2 w-full mb-2" placeholder="Subject"><input id="tt-tch" class="border p-2 w-full mb-2" placeholder="Teacher"><input id="tt-loc" class="border p-2 w-full mb-4" placeholder="Location"><div class="flex justify-end gap-2"><button id="c-tt" class="bg-gray-200 px-4 py-2 rounded">Cancel</button><button id="s-tt" class="bg-indigo-600 text-white px-4 py-2 rounded">Save</button></div></div></div>`;document.getElementById('c-tt').addEventListener('click',()=>document.getElementById('modal-container').innerHTML='');document.getElementById('s-tt').addEventListener('click',async()=>{await fetch(`${API_BASE_URL}/timetable`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({day:document.getElementById('tt-d').value,time:document.getElementById('tt-tm').value,subject:document.getElementById('tt-sub').value,teacher:document.getElementById('tt-tch').value,location:document.getElementById('tt-loc').value})});document.getElementById('modal-container').innerHTML='';await fetchTimetable();renderTimetableContainer(document.getElementById('main-content'));});}

    // --- NOTIFICATIONS ---
    function renderNotifications(c){c.innerHTML=`<div class="grid grid-cols-1 md:grid-cols-3 gap-6"><div class="md:col-span-1"><div class="bg-white p-6 rounded shadow"><h3 class="font-bold mb-4">Post</h3><textarea id="n-msg" class="w-full border p-2 mb-2" rows="3" placeholder="Msg"></textarea><select id="n-cls" class="w-full border p-2 mb-4"><option>All Classes</option>${classesData.map(x=>`<option>${x.name}</option>`).join('')}</select><button id="n-post" class="w-full bg-indigo-600 text-white py-2 rounded">Post</button></div></div><div class="md:col-span-2 space-y-4">${notificationsData.slice().reverse().map(n=>`<div class="bg-white p-4 shadow border-l-4 border-indigo-500"><p>${n.message}</p><div class="text-xs text-gray-500 mt-2 flex justify-between"><span>${n.className}</span><span>${n.timestamp}</span></div></div>`).join('')}</div></div>`;c.querySelector('#n-post').addEventListener('click',async()=>{const m=document.getElementById('n-msg').value,cl=document.getElementById('n-cls').value;if(!m)return;await fetch(`${API_BASE_URL}/notifications`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:m,className:cl,timestamp:new Date().toLocaleString()})});sendNotificationEmails(cl,m);await fetchNotifications();renderNotifications(c);});}
    function sendNotificationEmails(clsName,msg){let r=[];if(clsName==='All Classes')classesData.forEach(c=>r.push(...c.students));else{const c=classesData.find(x=>x.name===clsName);if(c)r=c.students;}const v=r.filter(s=>s.email&&s.email.includes('@'));if(v.length===0)return alert('Posted, but no emails found.');v.forEach(s=>emailjs.send(EMAILJS_SERVICE_ID,EMAILJS_TEMPLATE_ID,{to_email:s.email,student_name:s.name,from_name:currentUser.name,reply_to:currentUser.email,class_name:clsName,message:msg}));alert(`Sent emails to ${v.length} students.`);}

    // --- ATTENDANCE ---
    function renderAttendancePage(c) { const t = new Date(); const tn = t.toLocaleDateString('en-US', { weekday: 'long' }); const td = t.toISOString().split('T')[0]; const tc = timetableData.filter(x => x.day === tn); c.innerHTML = `<div class="grid grid-cols-1 lg:grid-cols-3 gap-6 h-full"><div class="lg:col-span-1 bg-white p-6 rounded shadow"><h2 class="font-bold mb-2">Mark Attendance</h2><p class="text-sm text-gray-500 mb-4">${tn}, ${td}</p>${tc.length?tc.map(x=>`<div class="p-4 border rounded mb-2 flex justify-between items-center hover:bg-indigo-50 cursor-pointer mab" data-s="${x.subject}"><div><b>${x.subject}</b><br><span class="text-xs">${x.time}</span></div><i data-lucide="chevron-right"></i></div>`).join(''):'<p>No classes today</p>'}</div><div class="lg:col-span-2 bg-white p-6 rounded shadow"><h2 class="font-bold mb-4">History</h2><div class="flex justify-between mb-2"><button id="pm"><i data-lucide="chevron-left"></i></button><span id="cmy" class="font-bold"></span><button id="nm"><i data-lucide="chevron-right"></i></button></div><div id="cg" class="calendar-grid"></div><div id="det" class="mt-4 hidden"><h4 class="font-bold border-b pb-2">Details</h4><div id="detc" class="mt-2"></div></div></div></div>`; let cd = new Date(); const rc = (d) => { const g = document.getElementById('cg'); document.getElementById('cmy').textContent = d.toLocaleDateString('en-US', { month: 'long', year: 'numeric' }); g.innerHTML = ''; const f = new Date(d.getFullYear(), d.getMonth(), 1).getDay(); const m = new Date(d.getFullYear(), d.getMonth() + 1, 0).getDate(); for (let i = 0; i < f; i++) g.appendChild(document.createElement('div')); for (let i = 1; i <= m; i++) { const e = document.createElement('div'); e.className = 'calendar-day border rounded p-1 flex items-center justify-center cursor-pointer hover:bg-gray-50'; e.textContent = i; e.onclick = () => ld(`${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(i).padStart(2,'0')}`); g.appendChild(e); } }; rc(cd); document.getElementById('pm').onclick = () => { cd.setMonth(cd.getMonth()-1); rc(cd); }; document.getElementById('nm').onclick = () => { cd.setMonth(cd.getMonth()+1); rc(cd); }; c.querySelectorAll('.mab').forEach(b => b.onclick = () => om(b.dataset.s, td)); lucide.createIcons(); }
    async function ld(d) { const dc = document.getElementById('det'); dc.classList.remove('hidden'); const c = document.getElementById('detc'); c.innerHTML = 'Loading...'; const r = await fetch(`${API_BASE_URL}/attendance?date=${d}`); const data = await r.json(); if (!data.length) return c.innerHTML = 'No records.'; const g = {}; data.forEach(x => { if (!g[x.className]) g[x.className] = { p: 0, a: 0 }; x.status === 'P' ? g[x.className].p++ : g[x.className].a++; }); c.innerHTML = Object.keys(g).map(k => `<div class="flex justify-between p-2 border-b"><span>${k}</span><span><span class="text-green-600">${g[k].p} P</span> / <span class="text-red-500">${g[k].a} A</span></span></div>`).join(''); }
    function om(cn, d) { const cl = classesData.find(c => c.name === cn); if (!cl) return alert('Class name in Timetable must match Class List name exactly.'); if (!cl.students.length) return alert('No students.'); document.getElementById('modal-container').innerHTML = `<div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"><div class="bg-white rounded-xl shadow-lg w-full max-w-xl max-h-[90vh] flex flex-col"><div class="p-6 border-b"><h2 class="font-bold text-xl">Attendance: ${cn}</h2></div><div class="p-6 overflow-y-auto flex-1 space-y-2">${cl.students.map(s=>`<div class="flex justify-between items-center p-2 bg-gray-50 rounded row" data-id="${s.id}" data-name="${s.name}"><span>${s.name}</span><div class="flex gap-1"><button class="ab p-2 rounded bg-green-100 active" data-v="P">P</button><button class="ab p-2 rounded bg-red-100" data-v="A">A</button></div></div>`).join('')}</div><div class="p-6 border-t text-right"><button id="sa" class="bg-indigo-600 text-white px-6 py-2 rounded">Save</button></div></div></div>`; const m = document.getElementById('modal-container'); m.querySelectorAll('.ab').forEach(b => b.onclick = (e) => { const r = e.target.closest('.row'); r.querySelectorAll('.ab').forEach(x => x.classList.remove('bg-green-600', 'bg-red-600', 'text-white', 'active')); e.target.classList.add('active', e.target.dataset.v === 'P' ? 'bg-green-600' : 'bg-red-600', 'text-white'); }); document.getElementById('sa').onclick = async () => { const r = []; m.querySelectorAll('.row').forEach(x => r.push({ studentId: x.dataset.id, studentName: x.dataset.name, className: cn, date: d, status: x.querySelector('.active').dataset.v })); await fetch(`${API_BASE_URL}/attendance`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(r) }); m.innerHTML = ''; alert('Saved'); }; }

    // --- SCORES ---
    function renderScoresPage(container) {
        const tabs = examsData.map(e => `<button class="exam-tab px-4 py-2 rounded-t-lg border-b-2 ${selectedExamId === e.id ? 'border-indigo-600 text-indigo-600 font-bold bg-indigo-50' : 'border-transparent text-gray-500 hover:text-gray-700'}" data-id="${e.id}">${e.title}</button>`).join('');
        container.innerHTML = `<div class="flex justify-between items-end border-b border-gray-200 mb-6"><div class="flex space-x-2 overflow-x-auto">${tabs}</div><button id="add-exam-btn" class="mb-2 bg-indigo-600 text-white px-4 py-2 rounded text-sm flex items-center gap-1"><i data-lucide="plus-circle" class="w-4 h-4"></i> New Exam</button></div><div id="scores-content"></div>`;
        container.querySelector('#add-exam-btn').addEventListener('click', openAddExamModal);
        container.querySelectorAll('.exam-tab').forEach(b => b.addEventListener('click', () => { selectedExamId = b.dataset.id; renderScoresPage(container); }));
        const content = document.getElementById('scores-content');
        if (examsData.length === 0) content.innerHTML = `<p class="text-center text-gray-500 py-10">No exams created yet.</p>`;
        else if (selectedExamId) renderExamEntry(content, selectedExamId);
        else if (examsData.length > 0) { selectedExamId = examsData[0].id; renderExamEntry(content, selectedExamId); }
        lucide.createIcons();
    }

    function renderExamEntry(container, examId) {
        const exam = examsData.find(e => e.id === examId);
        container.innerHTML = `<div class="bg-white p-6 rounded-xl shadow"><div class="flex justify-between mb-4"><h2 class="text-xl font-bold">${exam.title} <span class="text-sm font-normal text-gray-500">(Max: ${exam.totalMarks})</span></h2><button id="del-exam" class="text-red-500 text-sm hover:underline">Delete Exam</button></div><p class="mb-2 text-sm font-bold text-gray-600">Select Class to Enter Marks:</p><div class="flex gap-2 mb-6 flex-wrap">${classesData.map(c => `<button class="class-sel-btn border px-3 py-1 rounded hover:bg-gray-100" data-id="${c.id}">${c.name}</button>`).join('')}</div><div id="entry-table-area"></div></div>`;
        container.querySelector('#del-exam').addEventListener('click', async () => { if(confirm('Delete exam?')) { await fetch(`${API_BASE_URL}/exams/${examId}`, {method:'DELETE'}); await fetchExams(); selectedExamId = null; renderScoresPage(document.getElementById('main-content')); } });
        container.querySelectorAll('.class-sel-btn').forEach(b => b.addEventListener('click', (e) => { container.querySelectorAll('.class-sel-btn').forEach(x => x.classList.remove('bg-indigo-600', 'text-white')); e.target.classList.add('bg-indigo-600', 'text-white'); loadScoreTable(exam, e.target.dataset.id); }));
    }

    async function loadScoreTable(exam, classId) {
        const area = document.getElementById('entry-table-area');
        const cls = classesData.find(c => c.id === classId);
        let existingScores = [];
        try { const r = await fetch(`${API_BASE_URL}/scores?examId=${exam.id}`); if(r.ok) existingScores = await r.json(); } catch(e){}
        const rows = cls.students.sort((a,b)=>a.roll.localeCompare(b.roll, undefined, {numeric:true})).map(s => {
            const score = existingScores.find(sc => sc.studentId === s.id);
            return `<tr class="border-b score-row" data-sid="${s.id}"><td class="p-3">${s.roll}</td><td class="p-3 font-medium">${s.name}</td><td class="p-3"><input type="text" class="score-input border p-1 rounded w-20 text-center" value="${score ? score.marks : ''}" placeholder="-"> <span class="text-gray-400 text-sm">/ ${exam.totalMarks}</span></td></tr>`;
        }).join('');
        area.innerHTML = `<table class="w-full text-left mb-4"><thead><tr class="bg-gray-50"><th>Roll</th><th>Name</th><th>Marks</th></tr></thead><tbody>${rows}</tbody></table><div class="text-right"><button id="save-scores" class="bg-green-600 text-white px-6 py-2 rounded hover:bg-green-700">Save Scores</button></div>`;
        document.getElementById('save-scores').addEventListener('click', async () => {
            const payload = [];
            area.querySelectorAll('.score-row').forEach(r => { payload.push({ examId: exam.id, studentId: r.dataset.sid, marks: r.querySelector('.score-input').value || '0' }); });
            await fetch(`${API_BASE_URL}/scores`, { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload) }); alert('Scores Saved!');
        });
    }

    function openAddExamModal() {
        document.getElementById('modal-container').innerHTML = `<div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"><div class="bg-white p-6 rounded w-96"><h2 class="text-xl font-bold mb-4">Create Exam</h2><input id="ex-title" class="border p-2 w-full mb-2" placeholder="Title (e.g. Unit Test 1)"><input id="ex-total" type="number" class="border p-2 w-full mb-4" placeholder="Total Marks"><div class="flex justify-end gap-2"><button id="c-ex" class="bg-gray-200 px-4 py-2 rounded">Cancel</button><button id="s-ex" class="bg-indigo-600 text-white px-4 py-2 rounded">Save</button></div></div></div>`;
        document.getElementById('c-ex').addEventListener('click', () => document.getElementById('modal-container').innerHTML = '');
        document.getElementById('s-ex').addEventListener('click', async () => {
            await fetch(`${API_BASE_URL}/exams`, { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({ title: document.getElementById('ex-title').value, totalMarks: document.getElementById('ex-total').value }) });
            document.getElementById('modal-container').innerHTML = ''; await fetchExams(); renderScoresPage(document.getElementById('main-content'));
        });
    }


    checkSession();
});