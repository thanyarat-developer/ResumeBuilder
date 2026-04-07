// ฟังก์ชันเพิ่มช่องประสบการณ์งาน
function addExperience() {
    const container = document.getElementById('exp-list');
    const div = document.createElement('div');
    div.className = 'exp-item';
    div.innerHTML = `
        <input type="text" class="inYear" placeholder="ปีที่ทำ" oninput="updatePreview()">
        <textarea class="inDetail" placeholder="รายละเอียดงาน" oninput="updatePreview()"></textarea>
    `;
    container.appendChild(div);
}

// ฟังก์ชันสลับเทมเพลต
function changeTemplate(type) {
    const resume = document.getElementById('resume-to-print');
    resume.className = 'resume-paper ' + type;
}

function updatePreview() {
    // ข้อมูลส่วนตัว
    document.getElementById('outName').innerText = document.getElementById('inName').value || "ชื่อ-นามสกุล";
    document.getElementById('outRole').innerText = document.getElementById('inRole').value || "ตำแหน่งงาน";
    document.getElementById('outContact').innerText = document.getElementById('inContact').value || "ติดต่อ";

    // จัดการประสบการณ์งาน (Loop ตามจำนวนที่มี)
    const expRows = document.querySelectorAll('.exp-item');
    const outExpContainer = document.getElementById('outExpList');
    outExpContainer.innerHTML = "";

    expRows.forEach(row => {
        const year = row.querySelector('.inYear').value;
        const detail = row.querySelector('.inDetail').value;
        if (year || detail) {
            const html = `
                <div class="exp-row">
                    <div class="exp-year">${year}</div>
                    <div class="exp-desc">${detail}</div>
                </div>
            `;
            outExpContainer.innerHTML += html;
        }
    });

    // จัดการทักษะ
    const skills = document.getElementById('inSkills').value;
    const skillsContainer = document.getElementById('outSkills');
    skillsContainer.innerHTML = "";
    if (skills) {
        skills.split(',').forEach(s => {
            if(s.trim()) {
                skillsContainer.innerHTML += `<span class="skill-item">${s.trim()}</span>`;
            }
        });
    }
}

function exportPDF() {
    const element = document.getElementById('resume-to-print');
    html2pdf().from(element).set({
        margin: 0.5,
        filename: 'my_resume.pdf',
        jsPDF: { unit: 'in', format: 'a4' }
    }).save();
}
