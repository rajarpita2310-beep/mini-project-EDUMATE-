document.addEventListener('DOMContentLoaded', () => {

    // --- EMAILJS KEYS (FROM YOU) ---
    const EMAILJS_SERVICE_ID = 'service_3d2zafa';
    const EMAILJS_TEMPLATE_ID = 'template_6h83akp';
    const EMAILJS_PUBLIC_KEY = 'hgSP1X8fETYOSrLAb';

    // --- DATA STORE ---
    let classesData = [
        { 
            id: 'c1', 
            name: 'Grade 10 - Physics', 
            coordinatorName: 'Mr. Davis', 
            coordinatorPhone: '555-0101',
            students: [
                { id: 's101', name: 'Alice Johnson', roll: '101', 
                  profilePic: '', status: 'Day Scholar', email: 'alice@school.com', phone: '555-1111', 
                  parentEmail: 'johnson@family.com', parentPhone: '555-2222' 
                },
                { id: 's103', name: 'Charlie Brown', roll: '103', 
                  profilePic: '', status: 'Hosteller', email: 'charlie@school.com', phone: '555-1133', 
                  parentEmail: 'brown@family.com', parentPhone: '555-2244' 
                },
                { id: 's102', name: 'Bob Williams', roll: '102', 
                  profilePic: '', status: 'Day Scholar', email: 'bob@school.com', phone: '555-1122', 
                  parentEmail: 'williams@family.com', parentPhone: '555-2233' 
                }
            ]
        },
        { 
            id: 'c2', 
            name: 'Grade 12 - Chemistry Lab', 
            coordinatorName: 'Ms. Chen', 
            coordinatorPhone: '555-0202',
            students: [
                { id: 's201', name: 'Diana Miller', roll: '201', 
                  profilePic: '', status: 'Hosteller', email: 'diana@school.com', phone: '555-1144', 
                  parentEmail: 'miller@family.com', parentPhone: '555-2255' 
                }
            ]
        }
    ];

    let attendanceHistory = [
        { id: 1, date: '2025-11-04', className: 'Grade 10 - Physics', present: 2, absent: 1, total: 3 },
        { id: 2, date: '2025-11-04', className: 'Grade 12 - Chemistry Lab', present: 1, absent: 0, total: 1 },
    ];
    
    let attendanceDetails = [
        { recordId: 1, studentId: 's101', studentName: 'Alice Johnson', status: 'P' },
        { recordId: 1, studentId: 's102', studentName: 'Bob Williams', status: 'P' },
        { recordId: 1, studentId: 's103', studentName: 'Charlie Brown', status: 'A' },
        { recordId: 2, studentId: 's201', studentName: 'Diana Miller', status: 'P' },
    ];

    const dayOrder = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
    
    let timetableData = [
        { id: 't1', day: 'Monday', time: '09:00', subject: 'Physics', teacher: 'Mr. Davis', location: 'Room A101' },
        { id: 't2', day: 'Monday', time: '10:00', subject: 'Math', teacher: 'Ms. Chen', location: 'Room B203' },
        { id: 't3', day: 'Tuesday', time: '11:00', subject: 'Chemistry Lab', teacher: 'Ms. Chen', location: 'Lab 1' },
        { id: 't4', day: 'Friday', time: '14:00', subject: 'Physical Ed.', teacher: 'Mr. Singh', location: 'Gym' },
        { id: 't5', day: 'Tuesday', time: '09:00', subject: 'History', teacher: 'Mr. Singh', location: 'Room A101' },
    ];

    let notificationsData = [
        { 
            id: 'n1', 
            message: 'Welcome to the notifications panel! You can post announcements here.', 
            className: 'All Classes', 
            timestamp: new Date().toLocaleString() 
        }
    ];

    const teacherName = "Mr. Smith";
    let currentView = 'Dashboard'; 
    let currentTimetableView = 'list'; 

    // --- DOM Element Selectors ---
    const loginScreen = document.getElementById('login-screen');
    const appScreen = document.getElementById('app-screen');
    const loginForm = document.getElementById('login-form');
    const loginError = document.getElementById('login-error');

    // --- DYNAMIC HTML TEMPLATES ---
    
    const AppShellHTML = `
        <div class="flex h-screen bg-gray-100">
            <aside id="sidebar" class="w-64 bg-gray-800 text-white flex flex-col flex-shrink-0"></aside>
            <div class="flex-1 flex flex-col overflow-hidden">
                <header class="bg-white shadow-md">
                    <div class="px-6 h-16 flex items-center justify-between">
                        <h1 id="page-title" class="text-xl font-semibold text-gray-800">${currentView}</h1>
                        <span class="font-medium">Welcome, ${teacherName}!</span>
                    </div>
                </header>
                <main id="main-content" class="flex-1 overflow-x-hidden overflow-y-auto bg-gray-100 p-6"></main>
            </div>
        </div>
        <div id="modal-container"></div>
    `;

    const AddStudentModalHTML = `
        <div id="add-student-modal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md">
                <form id="add-student-form">
                    <input type="hidden" id="class-id-for-student" value=""> 
                    <div class="p-6 border-b"><h2 class="text-2xl font-bold">Add New Student</h2></div>
                    <div class="p-6 space-y-4">
                        <div>
                            <label for="student-name" class="block text-sm font-medium text-gray-700 mb-1">Student Name</label>
                            <input type="text" id="student-name" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500" required>
                        </div>
                        <div>
                            <label for="roll-number" class="block text-sm font-medium text-gray-700 mb-1">Roll Number</label>
                            <input type="text" id="roll-number" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500" required>
                        </div>
                    </div>
                    <div class="p-6 bg-gray-50 border-t rounded-b-2xl flex justify-end gap-4">
                        <button type="button" id="cancel-add-student" class="px-6 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300">Cancel</button>
                        <button type="submit" class="px-6 py-2 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700">Add Student</button>
                    </div>
                </form>
            </div>
        </div>`;

    const AttendanceModalHTML = `
        <div id="attendance-modal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div class="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] flex flex-col">
                <div class="p-6 border-b"><h2 class="text-2xl font-bold" id="modal-class-title">Take Attendance</h2><p class="text-gray-500">Mark the status for each student for today's session.</p></div>
                <div class="p-6 overflow-y-auto">
                    <div class="flex justify-end gap-2 mb-4">
                        <button class="mark-all-btn bg-green-500 text-white px-3 py-1 rounded-md text-xs hover:bg-green-600" data-status="P">Mark All Present</button>
                        <button class="mark-all-btn bg-red-500 text-white px-3 py-1 rounded-md text-xs hover:bg-red-600" data-status="A">Mark All Absent</button>
                    </div>
                    <div id="student-list" class="space-y-3"></div>
                </div>
                <div class="p-6 bg-gray-50 border-t rounded-b-2xl flex justify-end gap-4">
                    <button id="cancel-attendance" class="px-6 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300">Cancel</button>
                    <button id="save-attendance" class="px-6 py-2 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700">Save Attendance</button>
                </div>
            </div>
        </div>`;
    
    const AttendanceDetailsModalHTML = `
        <div id="attendance-details-modal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div class="bg-white rounded-2xl shadow-2xl w-full max-w-lg max-h-[90vh] flex flex-col">
                <div class="p-6 border-b">
                    <h2 class="text-2xl font-bold" id="details-modal-title">Attendance Details</h2>
                    <p class="text-gray-500" id="details-modal-subtitle">Date: 2025-11-04</p>
                </div>
                <div class="p-6 overflow-y-auto" id="details-student-list">
                    </div>
                <div class="p-6 bg-gray-50 border-t rounded-b-2xl flex justify-end">
                    <button id="close-details-modal" class="px-6 py-2 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700">Close</button>
                </div>
            </div>
        </div>`;

    const AddClassModalHTML = `
        <div id="add-class-modal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md">
                <form id="add-class-form">
                    <div class="p-6 border-b"><h2 class="text-2xl font-bold">Add New Class</h2></div>
                    <div class="p-6 space-y-4">
                        <div>
                            <label for="class-name" class="block text-sm font-medium text-gray-700 mb-1">Class Name</label>
                            <input type="text" id="class-name" placeholder="e.g., Grade 9 - History" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500" required>
                        </div>
                        <div>
                            <label for="coordinator-name" class="block text-sm font-medium text-gray-700 mb-1">Coordinator Name</label>
                            <input type="text" id="coordinator-name" placeholder="e.g., Ms. Patel" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500" required>
                        </div>
                        <div>
                            <label for="coordinator-phone" class="block text-sm font-medium text-gray-700 mb-1">Coordinator Phone</label>
                            <input type="tel" id="coordinator-phone" placeholder="e.g., 555-1234" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500" required>
                        </div>
                    </div>
                    <div class="p-6 bg-gray-50 border-t rounded-b-2xl flex justify-end gap-4">
                        <button type="button" id="cancel-add-class" class="px-6 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300">Cancel</button>
                        <button type="submit" class="px-6 py-2 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700">Add Class</button>
                    </div>
                </form>
            </div>
        </div>`;
    
    const ScheduleEntryModalHTML = `
        <div id="schedule-entry-modal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md">
                <form id="schedule-entry-form">
                    <input type="hidden" id="schedule-entry-id">
                    <input type="hidden" id="schedule-entry-day">
                    
                    <div class="p-6 border-b"><h2 id="schedule-modal-title" class="text-2xl font-bold">Add Class to Timetable</h2></div>
                    <div class="p-6 space-y-4">
                        <div>
                            <label for="schedule-time" class="block text-sm font-medium text-gray-700 mb-1">Time</label>
                            <input type="time" id="schedule-time" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500" required>
                        </div>
                        <div>
                            <label for="schedule-subject" class="block text-sm font-medium text-gray-700 mb-1">Subject</label>
                            <input type="text" id="schedule-subject" placeholder="e.g., Physics" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500" required>
                        </div>
                        <div>
                            <label for="schedule-teacher" class="block text-sm font-medium text-gray-700 mb-1">Teacher</label>
                            <input type="text" id="schedule-teacher" placeholder="e.g., Mr. Davis" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500">
                        </div>
                        <div>
                            <label for="schedule-location" class="block text-sm font-medium text-gray-700 mb-1">Location</label>
                            <input type="text" id="schedule-location" placeholder="e.g., Room A101" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500">
                        </div>
                    </div>
                    <div class="p-6 bg-gray-50 border-t rounded-b-2xl flex justify-end gap-4">
                        <button type="button" id="cancel-schedule-entry" class="px-6 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300">Cancel</button>
                        <button type="submit" class="px-6 py-2 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700">Save</button>
                    </div>
                </form>
            </div>
        </div>`;


    // --- PAGE CONTENT TEMPLATES ---
    const pageContent = {
        Dashboard: `
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                <div class="bg-white p-6 rounded-xl shadow-lg hover:shadow-xl transition-shadow col-span-1 md:col-span-2">
                    <div class="flex items-center mb-4"><div class="p-3 rounded-full bg-indigo-100 text-indigo-600 mr-4"><i data-lucide="calendar-days" class="w-6 h-6"></i></div><h2 class="text-xl font-semibold">Today's Classes</h2></div>
                    <div class="space-y-3">
                        <div class="flex justify-between items-center p-3 bg-gray-50 rounded-lg"><div><p class="font-semibold">Grade 10 - Physics</p><p class="text-sm text-gray-500">10:00 AM - 11:00 AM</p></div><button class="take-attendance-btn bg-green-500 text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-green-600 transition" data-class="Grade 10 - Physics">Take Attendance</button></div>
                        <div class="flex justify-between items-center p-3 bg-gray-50 rounded-lg"><div><p class="font-semibold">Grade 12 - Chemistry Lab</p><p class="text-sm text-gray-500">01:00 PM - 02:30 PM</p></div><button class="take-attendance-btn bg-green-500 text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-green-600 transition" data-class="Grade 12 - Chemistry Lab">Take Attendance</button></div>
                    </div>
                </div>
                <div class="bg-white p-6 rounded-xl shadow-lg hover:shadow-xl transition-shadow">
                    <div class="flex items-center mb-4"><div class="p-3 rounded-full bg-yellow-100 text-yellow-600 mr-4"><i data-lucide="clipboard-list" class="w-6 h-6"></i></div><h2 class="text-xl font-semibold">Pending Assignments</h2></div>
                    <div class="space-y-4"><div><div class="flex justify-between text-sm mb-1"><span class="font-medium">Physics - Ch. 4</span><span class="text-gray-500">18/30 Submitted</span></div><div class="w-full bg-gray-200 rounded-full h-2.5"><div class="bg-yellow-500 h-2.5 rounded-full" style="width: 60%"></div></div></div><div><div class="flex justify-between text-sm mb-1"><span class="font-medium">Chemistry - Lab Report</span><span class="text-gray-500">12/28 Submitted</span></div><div class="w-full bg-gray-200 rounded-full h-2.5"><div class="bg-yellow-500 h-2.5 rounded-full" style="width: 43%"></div></div></div></div>
                </div>
                <div class="bg-white p-6 rounded-xl shadow-lg hover:shadow-xl transition-shadow">
                    <div class="flex items-center mb-4"><div class="p-3 rounded-full bg-blue-100 text-blue-600 mr-4"><i data-lucide="upload-cloud" class="w-6 h-6"></i></div><h2 class="text-xl font-semibold">Recent Uploads</h2></div>
                    <ul class="space-y-2 list-disc list-inside text-gray-600"><li>Grade 10 Physics - Unit 5 Notes.pdf</li><li>Grade 12 Chemistry - Titration Guide.docx</li></ul>
                </div>
            </div>`,
        'Class Lists': `<div class="space-y-6" id="class-lists-content"></div>`,
        'Attendance': `<div class="bg-white p-6 rounded-xl shadow-lg" id="attendance-history-content"></div>`,
        'Notes & Resources': `<div class="bg-white p-6 rounded-xl shadow-lg"><h2 class="text-xl font-semibold">Notes & Resources</h2><p class="mt-2 text-gray-600">Teachers can upload and manage class notes and documents here.</p></div>`,
        'Assignments': `<div class="bg-white p-6 rounded-xl shadow-lg"><h2 class="text-xl font-semibold">Assignments</h2><p class="mt-2 text-gray-600">Create, track, and grade assignments from this section.</p></div>`,
        'Student Reports': `<div class="bg-white p-6 rounded-xl shadow-lg"><h2 class="text-xl font-semibold">Student Reports</h2><p class="mt-2 text-gray-600">Generate and view detailed performance reports for each student.</p></div>`,
        'Timetable': `<div id="timetable-wrapper"></div>`,
        'Notifications': `<div id="notifications-wrapper"></div>`,
    };


    // --- RENDER & LOGIC FUNCTIONS ---
    
    function renderAppShell() {
        appScreen.innerHTML = AppShellHTML;
        renderSidebar();
        renderPage(currentView);
    }
    
    function renderSidebar() {
        const sidebar = document.getElementById('sidebar');
        const links = [
            { name: 'Dashboard', icon: 'layout-dashboard' }, 
            { name: 'Class Lists', icon: 'users' },
            { name: 'Attendance', icon: 'user-check' }, 
            { name: 'Notes & Resources', icon: 'book-open' },
            { name: 'Assignments', icon: 'clipboard-list' }, 
            { name: 'Student Reports', icon: 'file-bar-chart' },
            { name: 'Timetable', icon: 'calendar' }, 
            { name: 'Notifications', icon: 'bell' }
        ];
        const navLinksHTML = links.map(link => `
            <a href="#" class="sidebar-link flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-colors duration-200 hover:bg-gray-700 ${currentView === link.name ? 'active' : ''}" data-page="${link.name}">
                <i data-lucide="${link.icon}" class="w-5 h-5 mr-3"></i> ${link.name}
            </a>`).join('');

        sidebar.innerHTML = `
            <div class="h-16 flex items-center justify-center text-2xl font-bold text-white border-b border-gray-700">EduMate</div>
            <nav class="flex-1 px-2 py-4 space-y-2">${navLinksHTML}</nav>
            <div class="px-2 py-4 border-t border-gray-700">
                <button id="logout-button" class="w-full flex items-center px-4 py-2.5 text-sm font-medium rounded-lg transition-colors duration-200 hover:bg-red-600">
                    <i data-lucide="log-out" class="w-5 h-5 mr-3"></i> Logout
                </button>
            </div>`;
        sidebar.addEventListener('click', handleSidebarNavClick);
        document.getElementById('logout-button').addEventListener('click', showLoginScreen);
    }

    function renderPage(pageName) {
        currentView = pageName;
        document.getElementById('page-title').textContent = pageName;
        const mainContent = document.getElementById('main-content');
        mainContent.innerHTML = pageContent[pageName] || `<p>Page not found</p>`;
        
        if (pageName === 'Class Lists') {
            renderClassListsPage(); 
        }
        if (pageName === 'Attendance') {
            renderAttendanceHistory();
        }
        if (pageName === 'Timetable') {
            renderTimetableContainer();
        }
        if (pageName === 'Notifications') {
            renderNotificationsPage();
        }

        document.querySelectorAll('.sidebar-link').forEach(l => {
            l.classList.toggle('active', l.dataset.page === pageName);
        });

        lucide.createIcons();
        mainContent.querySelectorAll('.take-attendance-btn').forEach(button => {
            button.addEventListener('click', handleTakeAttendanceClick);
        });
    }

    // --- 'CLASS LISTS' PAGE FUNCTIONS ---
    function renderClassListsPage() {
        const container = document.getElementById('class-lists-content');
        const classCardsHTML = classesData.map(cls => `
            <div class="bg-white p-6 rounded-xl shadow-lg">
                <div class="flex justify-between items-start">
                    <div>
                        <h3 class="text-xl font-bold text-indigo-700">${cls.name}</h3>
                        <p class="text-gray-600 mt-2">
                            <i data-lucide="user-circle" class="w-4 h-4 inline-block -mt-1 mr-1"></i>
                            Coordinator: <strong>${cls.coordinatorName}</strong>
                        </p>
                        <p class="text-gray-600">
                            <i data-lucide="phone" class="w-4 h-4 inline-block -mt-1 mr-1"></i>
                            Phone: ${cls.coordinatorPhone}
                        </p>
                    </div>
                    <button class="delete-class-btn text-red-500 hover:text-red-700" data-class-id="${cls.id}">
                        <i data-lucide="trash-2" class="w-5 h-5"></i>
                    </button>
                </div>
                <div class="border-t mt-4 pt-4 flex justify-between items-center">
                    <span class="text-sm font-medium text-gray-700">${cls.students.length} Student(s)</span>
                    <button class="view-students-btn px-4 py-2 bg-indigo-600 text-white text-sm font-semibold rounded-lg hover:bg-indigo-700" data-class-id="${cls.id}">
                        View/Edit Students
                    </button>
                </div>
            </div>
        `).join('');

        container.innerHTML = `
            <div class="flex justify-between items-center mb-6">
                <h2 class="text-2xl font-bold text-gray-800">Your Classes</h2>
                <button id="add-class-btn" class="flex items-center gap-2 px-4 py-2 bg-green-600 text-white font-semibold rounded-lg hover:bg-green-700">
                   <i data-lucide="plus-circle" class="w-5 h-5"></i> Add New Class
                </button>
            </div>
            <div class="space-y-6">
                ${classesData.length > 0 ? classCardsHTML : `<p class="text-center text-gray-500">No classes found. Add your first class to get started!</p>`}
            </div>
        `;

        container.querySelector('#add-class-btn').addEventListener('click', openAddClassModal);
        container.querySelectorAll('.view-students-btn').forEach(btn => {
            btn.addEventListener('click', (e) => renderStudentListView(e.currentTarget.dataset.classId));
        });
        container.querySelectorAll('.delete-class-btn').forEach(btn => {
            btn.addEventListener('click', (e) => handleDeleteClass(e.currentTarget.dataset.classId));
        });
        
        lucide.createIcons();
    }

    function renderStudentListView(classId) {
        const container = document.getElementById('class-lists-content');
        const cls = classesData.find(c => c.id === classId);
        if (!cls) { renderClassListsPage(); return; }
        const sortedStudents = cls.students.sort((a, b) => a.roll.localeCompare(b.roll, undefined, { numeric: true }));
        const tableRows = sortedStudents.map(student => `
            <tr class="border-b hover:bg-gray-50">
                <td class="p-4">${student.roll}</td>
                <td class="p-4 font-medium">
                    <a href="#" class="view-student-profile-btn text-indigo-600 hover:underline" data-class-id="${classId}" data-student-id="${student.id}">
                        ${student.name}
                    </a>
                </td>
                <td class="p-4 text-right">
                    <button class="delete-student-btn text-red-500 hover:text-red-700" data-class-id="${classId}" data-student-id="${student.id}">
                        <i data-lucide="trash-2" class="w-4 h-4"></i>
                    </button>
                </td>
            </tr>
        `).join('');
        container.innerHTML = `
            <div class="mb-6">
                <button id="back-to-classes-btn" class="flex items-center gap-2 text-sm text-indigo-600 hover:underline font-medium">
                    <i data-lucide="arrow-left-circle" class="w-4 h-4"></i>
                    Back to All Classes
                </button>
            </div>
            <div class="bg-white p-6 rounded-xl shadow-lg">
                <div class="flex justify-between items-center mb-4">
                    <div>
                        <h2 class="text-2xl font-bold text-gray-800">${cls.name}</h2>
                        <p class="text-gray-600">Coordinator: ${cls.coordinatorName} (${cls.coordinatorPhone})</p>
                    </div>
                    <button id="add-student-btn" class="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700" data-class-id="${classId}">
                       <i data-lucide="user-plus" class="w-4 h-4"></i> Add Student
                    </button>
                </div>
                <div class="overflow-x-auto">
                    <table class="w-full text-sm text-left">
                        <thead class="bg-gray-50 text-xs text-gray-700 uppercase">
                            <tr><th class="p-4">Roll No.</th><th class="p-4">Name</th><th class="p-4"></th></tr>
                        </thead>
                        <tbody>
                            ${cls.students.length > 0 ? tableRows : `<tr><td colspan="3" class="text-center p-6 text-gray-500">No students in this class yet.</td></tr>`}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
        container.querySelector('#back-to-classes-btn').addEventListener('click', renderClassListsPage);
        container.querySelector('#add-student-btn').addEventListener('click', (e) => openAddStudentModal(e.currentTarget.dataset.classId));
        container.querySelectorAll('.delete-student-btn').forEach(btn => {
            btn.addEventListener('click', (e) => handleDeleteStudent(e.currentTarget.dataset.classId, e.currentTarget.dataset.studentId));
        });
        container.querySelectorAll('.view-student-profile-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault(); 
                renderStudentProfileView(e.currentTarget.dataset.classId, e.currentTarget.dataset.studentId);
            });
        });
        lucide.createIcons();
    }

    function renderStudentProfileView(classId, studentId) {
        const container = document.getElementById('class-lists-content');
        const cls = classesData.find(c => c.id === classId);
        if (!cls) { renderClassListsPage(); return; }
        const student = cls.students.find(s => s.id === studentId);
        if (!student) { renderStudentListView(classId); return; }
        const profilePicHTML = student.profilePic ? `...` : `...`; // (Omitted)
        container.innerHTML = `...`; // (Omitted)

        // (Re-pasting full function)
        const profilePicHTML_full = student.profilePic
            ? `<img src="${student.profilePic}" alt="Profile" class="w-32 h-32 rounded-full object-cover">`
            : `<div class="w-32 h-32 rounded-full bg-gray-200 flex items-center justify-center text-gray-500">
                   <i data-lucide="user" class="w-16 h-16"></i>
               </div>`;
        container.innerHTML = `
            <div class="mb-6">
                <button id="back-to-student-list-btn" class="flex items-center gap-2 text-sm text-indigo-600 hover:underline font-medium" data-class-id="${classId}">
                    <i data-lucide="arrow-left-circle" class="w-4 h-4"></i>
                    Back to Student List
                </button>
            </div>
            <div class="bg-white p-6 rounded-xl shadow-lg">
                <form id="student-profile-form">
                    <input type="hidden" id="profile-class-id" value="${classId}">
                    <input type="hidden" id="profile-student-id" value="${studentId}">
                    <div class="flex flex-col md:flex-row gap-6">
                        <div class="flex-shrink-0 flex flex-col items-center">
                            ${profilePicHTML_full}
                            <button type="button" id="change-picture-btn" class="mt-4 text-sm px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300">
                                Add/Change Picture
                            </button>
                        </div>
                        <div class="flex-grow">
                            <h2 class="text-3xl font-bold text-gray-800">${student.name}</h2>
                            <p class="text-lg text-gray-500 mb-6">Roll No: ${student.roll}</p>
                            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                    <label for="student-status" class="block text-sm font-medium text-gray-700 mb-1">Status</label>
                                    <select id="student-status" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500">
                                        <option value="Day Scholar" ${student.status === 'Day Scholar' ? 'selected' : ''}>Day Scholar</option>
                                        <option value="Hosteller" ${student.status === 'Hosteller' ? 'selected' : ''}>Hosteller</option>
                                    </select>
                                </div>
                                <div>
                                    <label for="student-phone" class="block text-sm font-medium text-gray-700 mb-1">Student Phone</label>
                                    <input type="tel" id="student-phone" value="${student.phone}" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500">
                                </div>
                                <div class="md:col-span-2">
                                    <label for="student-email" class="block text-sm font-medium text-gray-700 mb-1">Student Email</label>
                                    <input type="email" id="student-email" value="${student.email}" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500">
                                </div>
                                <hr class="md:col-span-2 my-2">
                                <div>
                                    <label for="parent-phone" class="block text-sm font-medium text-gray-700 mb-1">Parent Phone</label>
                                    <input type="tel" id="parent-phone" value="${student.parentPhone}" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500">
                                </div>
                                <div>
                                    <label for="parent-email" class="block text-sm font-medium text-gray-700 mb-1">Parent Email</label>
                                    <input type="email" id="parent-email" value="${student.parentEmail}" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500">
                                </div>
                                <div class="md:col-span-2 mt-2">
                                    <a href="tel:${student.parentPhone}" class="inline-flex items-center gap-2 px-4 py-2 bg-green-600 text-white font-semibold rounded-lg hover:bg-green-700">
                                        <i data-lucide="phone-call" class="w-4 h-4"></i>
                                        Call Parent (${student.parentPhone})
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="border-t mt-6 pt-6 flex justify-end">
                        <button type="submit" class="px-6 py-2 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700">
                            Save Profile
                        </button>
                    </div>
                </form>
            </div>
        `;

        container.querySelector('#back-to-student-list-btn').addEventListener('click', (e) => {
            renderStudentListView(e.currentTarget.dataset.classId);
        });
        container.querySelector('#change-picture-btn').addEventListener('click', () => {
            alert('Note: True file uploads require a back-end server. This is a placeholder.');
        });
        container.querySelector('#student-profile-form').addEventListener('submit', handleSaveProfile);
        lucide.createIcons();
    }


    // --- ATTENDANCE HISTORY FUNCTIONS ---
    function renderAttendanceHistory() {
        const container = document.getElementById('attendance-history-content');
        if (!container) return;
        let tableRows = attendanceHistory.map(record => {
            const percentage = record.total > 0 ? Math.round((record.present / record.total) * 100) : 0;
            return `
            <tr class="border-b hover:bg-gray-50">
                <td class="p-4">${record.date}</td>
                <td class="p-4 font-medium">${record.className}</td>
                <td class="p-4">
                    <span class="font-semibold">${record.present}</span> Present / 
                    <span class="font-semibold text-red-600">${record.absent}</span> Absent
                </td>
                <td class="p-4">
                    <div class="flex items-center gap-2">
                        <div class="w-full bg-gray-200 rounded-full h-2.5">
                            <div class="bg-indigo-600 h-2.5 rounded-full" style="width: ${percentage}%"></div>
                        </div>
                        <span class="text-sm text-gray-500 w-12 text-right">${percentage}%</span>
                    </div>
                </td>
                <td class="p-4 text-right">
                    <button class="view-attendance-details-btn text-indigo-600 hover:text-indigo-800 text-sm font-medium" data-record-id="${record.id}">
                        View Details
                    </button>
                </td>
            </tr>
        `;}).join('');
        if (attendanceHistory.length === 0) {
            tableRows = `<tr><td colspan="5" class="text-center p-6 text-gray-500">No attendance history found.</td></tr>`;
        }
        container.innerHTML = `
            <div class="flex justify-between items-center mb-4">
                <h2 class="text-xl font-semibold">Attendance History</h2>
            </div>
            <div class="overflow-x-auto">
                <table class="w-full text-sm text-left">
                    <thead class="bg-gray-50 text-xs text-gray-700 uppercase">
                        <tr>
                            <th class="p-4">Date</th>
                            <th class="p-4">Class</th>
                            <th class="p-4">Summary</th>
                            <th class="p-4">Percentage</th>
                            <th class="p-4"></th>
                        </tr>
                    </thead>
                    <tbody>
                        ${tableRows}
                    </tbody>
                </table>
            </div>
        `;
        container.querySelectorAll('.view-attendance-details-btn').forEach(btn => {
            btn.addEventListener('click', handleViewAttendanceDetails);
        });
    }

    function handleViewAttendanceDetails(e) {
        const recordId = e.currentTarget.dataset.recordId;
        const record = attendanceHistory.find(r => r.id == recordId);
        if (record) {
            openAttendanceDetailsModal(record);
        }
    }

    function openAttendanceDetailsModal(record) {
        openModal(AttendanceDetailsModalHTML);
        document.getElementById('details-modal-title').textContent = record.className;
        document.getElementById('details-modal-subtitle').textContent = `Date: ${record.date}`;
        populateAttendanceDetails(record.id);
        document.getElementById('close-details-modal').addEventListener('click', closeModal);
    }

    function populateAttendanceDetails(recordId) {
        const studentListContainer = document.getElementById('details-student-list');
        const details = attendanceDetails.filter(d => d.recordId == recordId);
        if (details.length === 0) {
            studentListContainer.innerHTML = `<p class="text-center text-gray-500">No student details found for this record.</p>`;
            return;
        }
        const studentRowsHTML = details.map(student => `...`).join(''); // (Omitted)
        // (Re-pasting)
        const studentRowsHTML_full = details.map(student => {
            const isPresent = student.status === 'P';
            const statusClass = isPresent ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800';
            const statusText = isPresent ? 'Present' : 'Absent';
            return `
            <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg mb-3">
                <p class="font-medium">${student.studentName}</p>
                <span class="px-3 py-1 rounded-full text-xs font-semibold ${statusClass}">
                    ${statusText}
                </span>
            </div>
            `;
        }).join('');
        studentListContainer.innerHTML = studentRowsHTML_full;
    }
    // --- END OF ATTENDANCE HISTORY FUNCTIONS ---


    // --- TIMETABLE PAGE FUNCTIONS ---
    
    function renderTimetableContainer() {
        const container = document.getElementById('timetable-wrapper');
        const isListActive = currentTimetableView === 'list';
        const isTableActive = currentTimetableView === 'table';

        container.innerHTML = `
            <div class="flex justify-end items-center mb-4">
                <div class="p-1 bg-gray-200 rounded-lg flex gap-1">
                    <button id="timetable-list-view-btn" class="flex items-center gap-2 px-3 py-1 text-sm font-medium rounded-md ${isListActive ? 'bg-white text-indigo-700 shadow' : 'text-gray-600'}">
                        <i data-lucide="list" class="w-4 h-4"></i> List View
                    </button>
                    <button id="timetable-table-view-btn" class="flex items-center gap-2 px-3 py-1 text-sm font-medium rounded-md ${isTableActive ? 'bg-white text-indigo-700 shadow' : 'text-gray-600'}">
                        <i data-lucide="layout-grid" class="w-4 h-4"></i> Table View
                    </button>
                </div>
            </div>
            <div id="timetable-content" class="space-y-8"></div>
        `;
        
        container.querySelector('#timetable-list-view-btn').addEventListener('click', () => {
            currentTimetableView = 'list';
            renderTimetableContainer(); 
        });
        container.querySelector('#timetable-table-view-btn').addEventListener('click', () => {
            currentTimetableView = 'table';
            renderTimetableContainer(); 
        });

        if (isListActive) {
            renderTimetableList();
        } else {
            renderTimetableTable();
        }
        
        lucide.createIcons();
    }

    function renderTimetableList() {
        const container = document.getElementById('timetable-content');
        if (!container) return; 
        
        let allDaysHTML = '';
        for (const day of dayOrder) {
            const dayEntries = timetableData
                .filter(entry => entry.day === day)
                .sort((a, b) => a.time.localeCompare(b.time)); 
            let entriesHTML = '';
            if (dayEntries.length > 0) {
                entriesHTML = dayEntries.map(entry => `
                    <div class="p-4 bg-gray-50 border border-gray-100 rounded-lg flex flex-col md:flex-row justify-between items-start md:items-center shadow-sm hover:shadow-md transition">
                        <div class="flex flex-col text-gray-700">
                            <p class="text-base font-semibold text-indigo-600">[${entry.time}] ${entry.subject}</p>
                            <p class="text-sm">Teacher: ${entry.teacher || 'N/A'} | Location: ${entry.location || 'N/A'}</p>
                        </div>
                        <div class="flex space-x-2 mt-2 md:mt-0">
                            <button class="edit-schedule-btn p-2 text-indigo-500 hover:text-indigo-700 transition" data-entry-id="${entry.id}">
                                <i data-lucide="edit-2" class="w-4 h-4"></i>
                            </button>
                            <button class="delete-schedule-btn p-2 text-red-500 hover:text-red-700 transition" data-entry-id="${entry.id}">
                                <i data-lucide="x" class="w-4 h-4"></i>
                            </button>
                        </div>
                    </div>
                `).join('');
            } else {
                entriesHTML = `<p class="text-sm text-gray-500 italic p-2">No classes scheduled for ${day}.</p>`;
            }

            allDaysHTML += `
                <div class="bg-white p-6 rounded-xl shadow-lg">
                    <h3 class="text-xl font-bold text-gray-800 mb-3">${day}</h3>
                    <div class="space-y-3">
                        ${entriesHTML}
                        <button class="add-schedule-btn w-full flex items-center justify-center text-sm px-4 py-2 bg-indigo-100 text-indigo-600 rounded-lg hover:bg-indigo-200 transition mt-2 border-dashed border-2 border-indigo-300" data-day="${day}">
                            <i data-lucide="plus" class="w-4 h-4 mr-2"></i> Add Class to ${day}
                        </button>
                    </div>
                </div>
            `;
        }
        container.innerHTML = allDaysHTML;

        container.querySelectorAll('.add-schedule-btn').forEach(btn => {
            btn.addEventListener('click', (e) => openAddScheduleModal(e.currentTarget.dataset.day));
        });
        container.querySelectorAll('.edit-schedule-btn').forEach(btn => {
            btn.addEventListener('click', (e) => openEditScheduleModal(e.currentTarget.dataset.entryId));
        });
        container.querySelectorAll('.delete-schedule-btn').forEach(btn => {
            btn.addEventListener('click', (e) => handleDeleteSchedule(e.currentTarget.dataset.entryId));
        });

        lucide.createIcons();
    }

    function renderTimetableTable() {
        const container = document.getElementById('timetable-content');
        if (!container) return; 

        const timeSlots = [...new Set(timetableData.map(e => e.time))].sort((a, b) => a.localeCompare(b));
        let headerHTML = '<tr><th class="p-2 border border-gray-300 w-24">Time</th>';
        for (const day of dayOrder) {
            headerHTML += `<th class="p-2 border border-gray-300">${day}</th>`;
        }
        headerHTML += '</tr>';

        let bodyHTML = '';
        if (timeSlots.length === 0) {
            bodyHTML = `<tr><td colspan="${dayOrder.length + 1}" class="p-6 text-center text-gray-500">No classes scheduled in the timetable.</td></tr>`;
        } else {
            for (const time of timeSlots) {
                bodyHTML += '<tr>';
                bodyHTML += `<td class="p-2 border border-gray-300 text-center font-semibold text-indigo-600">${time}</td>`;
                for (const day of dayOrder) {
                    const entry = timetableData.find(e => e.day === day && e.time === time);
                    if (entry) {
                        bodyHTML += `
                            <td class="p-2 border border-gray-300 align-top text-xs bg-indigo-50">
                                <p class="font-bold text-indigo-700">${entry.subject}</p>
                                <p class="text-gray-600">${entry.teacher}</p>
                                <p class="text-gray-500 italic">${entry.location}</p>
                            </td>`;
                    } else {
                        bodyHTML += `<td class="p-2 border border-gray-300 h-20 bg-gray-50"></td>`;
                    }
                }
                bodyHTML += '</tr>';
            }
        }
        
        container.innerHTML = `
            <div class="bg-white p-6 rounded-xl shadow-lg">
                <p class="text-sm text-gray-500 mb-4">
                    This is a read-only view. To add, edit, or delete classes, please use the "List View".
                </p>
                <div class="overflow-x-auto">
                    <table class="w-full border-collapse border border-gray-300 text-sm">
                        <thead class="bg-gray-100">${headerHTML}</thead>
                        <tbody>${bodyHTML}</tbody>
                    </table>
                </div>
            </div>
        `;
    }


    // --- NOTIFICATIONS PAGE FUNCTIONS ---

    function renderNotificationsPage() {
        const container = document.getElementById('notifications-wrapper');
        if (!container) return;

        const classOptions = classesData.map(cls => 
            `<option value="${cls.name}">${cls.name}</option>`
        ).join('');

        const notificationList = notificationsData
            .slice() 
            .reverse() 
            .map(notif => `
                <div class="bg-white p-4 rounded-xl shadow-md border border-gray-200">
                    <p class="text-gray-800">${notif.message}</p>
                    <div class="flex justify-between items-center text-sm text-gray-500 mt-3 pt-3 border-t">
                        <span class="font-medium px-2 py-0.5 rounded-full bg-indigo-100 text-indigo-700">${notif.className}</span>
                        <span>${notif.timestamp}</span>
                    </div>
                    <div classbutton="mt-3">
                        <button class="send-email-btn text-sm flex items-center gap-2 px-3 py-1 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
                                data-message="${notif.message}" 
                                data-class-name="${notif.className}">
                            <i data-lucide="mail" class="w-4 h-4"></i>
                            Send as Email
                        </button>
                    </div>
                </div>
            `).join('');

        container.innerHTML = `
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div class="md:col-span-1">
                    <div class="bg-white p-6 rounded-xl shadow-lg sticky top-6">
                        <h2 class="text-xl font-bold text-gray-800 mb-4">Post New Announcement</h2>
                        <form id="notification-form">
                            <div class="space-y-4">
                                <div>
                                    <label for="notification-message" class="block text-sm font-medium text-gray-700 mb-1">Message</label>
                                    <textarea id="notification-message" rows="4" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500" placeholder="e.g., Extra class on Friday..." required></textarea>
                                </div>
                                <div>
                                    <label for="notification-class" class="block text-sm font-medium text-gray-700 mb-1">For Class</label>
                                    <select id="notification-class" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500">
                                        <option value="All Classes">All Classes</option>
                                        ${classOptions}
                                    </select>
                                </div>
                                <button type="submit" class="w-full flex items-center justify-center gap-2 px-4 py-2 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700">
                                    <i data-lucide="send" class="w-4 h-4"></i> Post Notification
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
                <div class="md:col-span-2">
                    <h2 class="text-xl font-bold text-gray-800 mb-4">Recent Announcements</h2>
                    <div class="space-y-4">
                        ${notificationList}
                    </div>
                </div>
            </div>
        `;

        container.querySelector('#notification-form').addEventListener('submit', handleAddNotification);
        
        // Add listener for all new email buttons
        container.querySelectorAll('.send-email-btn').forEach(btn => {
            btn.addEventListener('click', (e) => handleEmailNotification(e.currentTarget.dataset));
        });
        
        lucide.createIcons();
    }


    // --- MODAL & FORM FUNCTIONS ---

    function openModal(modalHTML) {
        document.getElementById('modal-container').innerHTML = modalHTML;
    }

    function closeModal() {
        document.getElementById('modal-container').innerHTML = '';
    }

    function openAddClassModal() {
        openModal(AddClassModalHTML);
        document.getElementById('add-class-form').addEventListener('submit', handleAddClass);
        document.getElementById('cancel-add-class').addEventListener('click', closeModal);
    }

    function openAddStudentModal(classId) {
        openModal(AddStudentModalHTML);
        document.getElementById('class-id-for-student').value = classId; 
        document.getElementById('add-student-form').addEventListener('submit', handleAddStudent);
        document.getElementById('cancel-add-student').addEventListener('click', closeModal);
    }
    
    function openAttendanceModal(className) {
        openModal(AttendanceModalHTML);
        document.getElementById('modal-class-title').textContent = `Attendance for ${className}`;
        populateStudentList(className); 
        document.getElementById('cancel-attendance').addEventListener('click', closeModal);
        document.getElementById('save-attendance').addEventListener('click', handleSaveAttendanceClick);
        document.getElementById('student-list').addEventListener('click', (e) => { if (e.target.classList.contains('status-btn')) handleStatusBtnClick(e); });
        document.querySelectorAll('.mark-all-btn').forEach(button => button.addEventListener('click', handleMarkAllClick));
    }

    function populateStudentList(className) {
        const studentListContainer = document.getElementById('student-list');
        studentListContainer.innerHTML = '';
        const classObj = classesData.find(c => c.name === className);
        if (!classObj || classObj.students.length === 0) {
            studentListContainer.innerHTML = `<p class="text-center text-gray-500">No students found for this class. Please add students in the 'Class Lists' page.</p>`;
            return;
        }
        const sortedStudents = classObj.students.sort((a, b) => a.roll.localeCompare(b.roll, undefined, { numeric: true }));
        sortedStudents.forEach(student => {
            const studentRow = `
                <div class="student-row flex items-center justify-between p-3 bg-gray-50 rounded-lg" data-student-id="${student.id}">
                    <div><p class="font-medium">${student.name}</p><p class="text-sm text-gray-500">Roll No: ${student.roll}</p></div>
                    <div class="flex gap-2 attendance-btn-group">
                        <button class="status-btn w-10 h-10 rounded-full font-bold text-white bg-green-500 hover:bg-green-600 transition" data-status="P">P</button>
                        <button class="status-btn w-10 h-10 rounded-full font-bold text-white bg-red-500 hover:bg-red-600 transition" data-status="A">A</button>
                    </div>
                </div>`;
            studentListContainer.insertAdjacentHTML('beforeend', studentRow);
        });
    }

    function openAddScheduleModal(day) {
        openModal(ScheduleEntryModalHTML);
        document.getElementById('schedule-modal-title').textContent = `Add Class to ${day}`;
        document.getElementById('schedule-entry-day').value = day;
        document.getElementById('schedule-entry-form').addEventListener('submit', handleAddOrEditSchedule);
        document.getElementById('cancel-schedule-entry').addEventListener('click', closeModal);
    }

    function openEditScheduleModal(entryId) {
        const entry = timetableData.find(e => e.id === entryId);
        if (!entry) { alert('Error: Could not find schedule entry.'); return; }
        openModal(ScheduleEntryModalHTML);
        document.getElementById('schedule-modal-title').textContent = `Edit Class on ${entry.day}`;
        document.getElementById('schedule-entry-id').value = entry.id;
        document.getElementById('schedule-entry-day').value = entry.day;
        document.getElementById('schedule-time').value = entry.time;
        document.getElementById('schedule-subject').value = entry.subject;
        document.getElementById('schedule-teacher').value = entry.teacher;
        document.getElementById('schedule-location').value = entry.location;
        document.getElementById('schedule-entry-form').addEventListener('submit', handleAddOrEditSchedule);
        document.getElementById('cancel-schedule-entry').addEventListener('click', closeModal);
    }

    
    // --- EVENT HANDLERS ---
    
    function handleLoginFormSubmit(event) {
        event.preventDefault();
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        if (email.trim() === '' || password.trim() === '') {
            loginError.classList.remove('hidden');
            return;
        }
        loginError.classList.add('hidden');
        loginScreen.classList.add('hidden');
        appScreen.classList.remove('hidden');
        renderAppShell();
        
        // --- INITIALIZE EMAILJS ---
        // We do this *after* login
        try {
            emailjs.init(EMAILJS_PUBLIC_KEY);
            console.log("EmailJS Initialized.");
        } catch (e) {
            console.error("Failed to initialize EmailJS:", e);
            alert("Email service is not configured correctly. Please check API keys.");
        }
    }

    function showLoginScreen() {
        document.getElementById('email').value = '';
        document.getElementById('password').value = '';
        appScreen.classList.add('hidden');
        appScreen.innerHTML = '';
        loginScreen.classList.remove('hidden');
    }
    
    function handleSidebarNavClick(e) {
        const link = e.target.closest('.sidebar-link');
        if (link && link.dataset.page !== currentView) {
            renderPage(link.dataset.page);
        }
    }
    
    function handleTakeAttendanceClick(e) {
        openAttendanceModal(e.target.dataset.class);
    }
    
    function handleAddClass(e) {
        e.preventDefault();
        const newClass = {
            id: 'c' + (classesData.length + 1) + Date.now(), 
            name: document.getElementById('class-name').value,
            coordinatorName: document.getElementById('coordinator-name').value,
            coordinatorPhone: document.getElementById('coordinator-phone').value,
            students: [] 
        };
        classesData.push(newClass);
        closeModal();
        renderClassListsPage(); 
    }

    function handleDeleteClass(classId) {
        if (confirm('Are you sure you want to delete this entire class and all its students?')) {
            classesData = classesData.filter(c => c.id !== classId);
            renderClassListsPage(); 
        }
    }

    function handleAddStudent(e) {
        e.preventDefault();
        const classId = document.getElementById('class-id-for-student').value;
        const name = document.getElementById('student-name').value;
        const roll = document.getElementById('roll-number').value;
        const classObj = classesData.find(c => c.id === classId);
        if (classObj) {
            const newStudent = {
                id: 's' + (classObj.students.length + 1) + Date.now(), 
                name, roll, profilePic: '', status: 'Day Scholar',
                email: '', phone: '', parentEmail: '', parentPhone: ''
            };
            classObj.students.push(newStudent);
            closeModal();
            renderStudentListView(classId); 
        } else {
            alert('Error: Class not found.');
            closeModal();
        }
    }

    function handleDeleteStudent(classId, studentId) {
        const classObj = classesData.find(c => c.id === classId);
        if (classObj && confirm('Are you sure you want to remove this student?')) {
            classObj.students = classObj.students.filter(s => s.id !== studentId);
            renderStudentListView(classId); 
        }
    }

    function handleSaveProfile(e) {
        e.preventDefault();
        const classId = document.getElementById('profile-class-id').value;
        const studentId = document.getElementById('profile-student-id').value;
        const cls = classesData.find(c => c.id === classId);
        if (!cls) { alert('Error: Class not found'); return; }
        const student = cls.students.find(s => s.id === studentId);
        if (!student) { alert('Error: Student not found'); return; }
        student.status = document.getElementById('student-status').value;
        student.phone = document.getElementById('student-phone').value;
        student.email = document.getElementById('student-email').value;
        student.parentPhone = document.getElementById('parent-phone').value;
        student.parentEmail = document.getElementById('parent-email').value;
        alert('Profile Saved!');
        renderStudentProfileView(classId, studentId);
    }
    
    function handleMarkAllClick(e) {
        const status = e.target.dataset.status;
        document.querySelectorAll('.student-row').forEach(row => {
            row.querySelectorAll('.status-btn').forEach(btn => btn.classList.remove('active'));
            const btnToActivate = row.querySelector(`.status-btn[data-status="${status}"]`);
            if (btnToActivate) btnToActivate.classList.add('active');
        });
    }

    function handleStatusBtnClick(e) {
        const button = e.target;
        const parentGroup = button.parentElement;
        parentGroup.querySelectorAll('.status-btn').forEach(btn => btn.classList.remove('active'));
        button.classList.add('active');
    }

    function handleSaveAttendanceClick() {
        const attendanceData = [];
        document.querySelectorAll('.student-row').forEach(row => {
            const studentId = row.dataset.studentId;
            const activeBtn = row.querySelector('.status-btn.active');
            const status = activeBtn ? activeBtn.dataset.status : 'Unmarked';
            attendanceData.push({ studentId, status });
        });
        console.log('--- Saving Attendance Data (simulated) ---');
        console.table(attendanceData);
        alert('Attendance data has been captured and logged to the browser console!');
        closeModal();
    }
    
    function handleAddOrEditSchedule(e) {
        e.preventDefault();
        const entryId = document.getElementById('schedule-entry-id').value;
        const entryData = {
            day: document.getElementById('schedule-entry-day').value,
            time: document.getElementById('schedule-time').value,
            subject: document.getElementById('schedule-subject').value,
            teacher: document.getElementById('schedule-teacher').value,
            location: document.getElementById('schedule-location').value,
        };
        if (entryId) {
            const index = timetableData.findIndex(e => e.id === entryId);
            if (index > -1) {
                timetableData[index] = { ...timetableData[index], ...entryData };
            }
        } else {
            entryData.id = 't' + Date.now(); 
            timetableData.push(entryData);
        }
        closeModal();
        renderTimetableContainer(); 
    }

    function handleDeleteSchedule(entryId) {
        if (confirm('Are you sure you want to delete this class from the timetable?')) {
            timetableData = timetableData.filter(e => e.id !== entryId);
            renderTimetableContainer(); 
        }
    }
    
    function handleAddNotification(e) {
        e.preventDefault();
        const message = document.getElementById('notification-message').value;
        const className = document.getElementById('notification-class').value;
        if (message.trim() === '') return;
        const newNotification = {
            id: 'n' + Date.now(),
            message: message,
            className: className,
            timestamp: new Date().toLocaleString()
        };
        notificationsData.push(newNotification);
        renderNotificationsPage();
    }

    // --- NEW EMAIL NOTIFICATION HANDLER ---
    async function handleEmailNotification(dataset) {
        const message = dataset.message;
        const className = dataset.className;
        
        let studentsToEmail = [];

        if (className === 'All Classes') {
            // Get all students from all classes
            classesData.forEach(cls => {
                studentsToEmail.push(...cls.students);
            });
        } else {
            // Get students from the specific class
            const cls = classesData.find(c => c.name === className);
            if (cls) {
                studentsToEmail = cls.students;
            }
        }

        if (studentsToEmail.length === 0) {
            alert('No students found for this notification.');
            return;
        }

        alert(`Preparing to send ${studentsToEmail.length} email(s)...`);

        let successCount = 0;
        let errorCount = 0;

        // Loop and send one email at a time
        for (const student of studentsToEmail) {
            if (!student.email) {
                console.warn(`Skipping student ${student.name}: no email on file.`);
                errorCount++;
                continue;
            }

            const templateParams = {
                student_name: student.name,
                student_email: student.email,
                class_name: className,
                subject: `EduMate Announcement: ${className}`,
                message: message
            };

            try {
                // This is the function that sends the email
                await emailjs.send(EMAILJS_SERVICE_ID, EMAILJS_TEMPLATE_ID, templateParams);
                console.log(`Successfully sent email to ${student.name}`);
                successCount++;
            } catch (err) {
                console.error(`Failed to send email to ${student.name}:`, err);
                errorCount++;
            }
        }

        // Show final report
        alert(`Email campaign finished.\n\nSuccessfully sent: ${successCount}\nFailed to send: ${errorCount}`);
    }

    
    // --- INITIALIZE APP ---
    loginForm.addEventListener('submit', handleLoginFormSubmit);
    lucide.createIcons();
});