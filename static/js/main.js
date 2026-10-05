const studentProfiles = {
    sarah: {
        name: "Sarah Miller",
        class: "Grade 12 - Advanced Placement",
        gender: "Female",
        attendance: 95,
        studyHours: 25,
        previousGrade: 90,
        extracurricular: 2,
        parentalSupport: "High"
    },
    john: {
        name: "John Davis",
        class: "Grade 10 - Section A",
        gender: "Male",
        attendance: 85,
        studyHours: 15,
        previousGrade: 78,
        extracurricular: 1,
        parentalSupport: "Medium"
    },
    daniel: {
        name: "Daniel Smith",
        class: "Grade 9 - Section C",
        gender: "Male",
        attendance: 70,
        studyHours: 8,
        previousGrade: 60,
        extracurricular: 0,
        parentalSupport: "Low"
    }
};

function fillProfile(key) {
    const profile = studentProfiles[key];
    if (!profile) return;

    document.getElementById('student_name').value = profile.name;
    document.getElementById('student_class').value = profile.class;
    document.getElementById('gender').value = profile.gender;
    document.getElementById('attendance_rate').value = profile.attendance;
    document.getElementById('study_hours').value = profile.studyHours;
    document.getElementById('previous_grade').value = profile.previousGrade;
    document.getElementById('extracurricular').value = profile.extracurricular;
    document.getElementById('parental_support').value = profile.parentalSupport;

    const formCard = document.querySelector('.card');
    if (formCard) {
        formCard.classList.add('border-primary');
        setTimeout(() => formCard.classList.remove('border-primary'), 400);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('predictionForm');
    if (form) {
        form.addEventListener('submit', (event) => {
            const name = document.getElementById('student_name').value.trim();
            const studentClass = document.getElementById('student_class').value.trim();

            if (!name || !studentClass) {
                event.preventDefault();
                alert("Please fill in both Student Name and Class for reference.");
            }
        });
    }
});
